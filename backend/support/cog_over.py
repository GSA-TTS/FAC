from collections import defaultdict
import logging

from django.db.models.functions import Cast
from django.db.models import BigIntegerField, Q

from support.models import CognizantBaseline, CognizantAssignment
from dissemination.models import General, MigrationInspectionRecord, FederalAward

logger = logging.getLogger(__name__)


COG_LIMIT = 50_000_000
DA_THRESHOLD_FACTOR = 0.25


def compute_cog_over(federal_awards, submission_status, auditee_ein, auditee_uei):
    """
    Compute cog or oversight agency for the sac.
    Return tuple (cog_agency, oversight_agency)

    WIP:
    - sac.federal_awards
    - sac.submission_status
    - sac.ein
    - sac.auditee_uei
    """
    if not federal_awards:
        logger.warning(
            f"Trying to determine cog_over for a sac with zero awards with status = {submission_status}."
        )
        return (None, None)
    awards = federal_awards["FederalAwards"]
    total_amount_expended = awards.get("total_amount_expended")
    cognizant_agency = oversight_agency = None
    (max_total_agency, max_da_agency) = calc_award_amounts(awards)

    agency = determine_agency(
        total_amount_expended,
        max_total_agency,
        max_da_agency,
    )

    if total_amount_expended <= COG_LIMIT:
        oversight_agency = agency
        # logger.warning("Assigning an oversight agenct", oversight_agency)
        return (cognizant_agency, oversight_agency)
    cognizant_agency = determine_hist_agency(auditee_ein, auditee_uei)
    if cognizant_agency:
        return (cognizant_agency, oversight_agency)
    cognizant_agency = agency
    return (cognizant_agency, oversight_agency)


def calc_award_amounts(awards):
    total_amount_agency = defaultdict(lambda: 0)
    total_da_amount_agency = defaultdict(lambda: 0)
    for award in awards["federal_awards"]:
        agency = award["program"]["federal_agency_prefix"]
        total_amount_agency[agency] += award["program"]["amount_expended"]
        if award["direct_or_indirect_award"]["is_direct"] == "Y":
            total_da_amount_agency[agency] += award["program"]["amount_expended"]
    return (
        prune_dict_to_max_values(total_amount_agency),
        prune_dict_to_max_values(total_da_amount_agency),
    )


def determine_agency(total_amount_expended, max_total_agency, max_da_agency):
    tie_breaker = defaultdict()
    for key, value in max_da_agency.items():
        if value >= DA_THRESHOLD_FACTOR * total_amount_expended:
            tie_breaker[key] = value + max_total_agency.get(key, 0)
    for agency in prune_dict_to_max_values(tie_breaker).keys():
        return agency
    for agency in max_total_agency.keys():
        return agency


def determine_hist_agency(ein, uei):
    report_id, dbkey = get_reportid_dbkey(ein, uei)

    cog_agency = lookup_baseline(ein, uei, dbkey)
    if cog_agency:
        return cog_agency
    (gen_count, total_amount_expended) = get_2019_gen(ein, report_id)
    if gen_count != 1:
        return None
    cfdas = get_2019_cfdas(ein, report_id)
    if not cfdas:
        # logger.warning("Found no cfda data for dbkey {dbkey} in 2019")
        return None
    (max_total_agency, max_da_agency) = calc_cfda_amounts(cfdas)
    cognizant_agency = determine_agency(
        total_amount_expended,
        max_total_agency,
        max_da_agency,
    )
    return cognizant_agency


def get_reportid_dbkey(ein, uei):
    try:
        report_id = General.objects.values_list("report_id", flat=True).get(
            Q(auditee_ein=ein), Q(auditee_uei=uei), Q(audit_year="2022")
        )
    except (General.DoesNotExist, General.MultipleObjectsReturned):
        report_id = None
        dbkey = None
        return report_id, dbkey

    try:
        dbkey = MigrationInspectionRecord.objects.values_list("dbkey", flat=True).get(
            Q(report_id=report_id), Q(audit_year="2022")
        )[:]
    except (
        MigrationInspectionRecord.DoesNotExist,
        MigrationInspectionRecord.MultipleObjectsReturned,
    ):
        dbkey = None
    return report_id, dbkey


def lookup_baseline(ein, uei, dbkey):
    try:
        cognizant_agency = CognizantBaseline.objects.values_list(
            "cognizant_agency", flat=True
        ).get(
            Q(is_active=True)
            & ((Q(ein=ein) & Q(dbkey=dbkey)) | (Q(ein=ein) & Q(uei=uei)))
        )[
            :
        ]
    except (CognizantBaseline.DoesNotExist, CognizantBaseline.MultipleObjectsReturned):
        cognizant_agency = None
    return cognizant_agency


def get_2019_gen(ein, report_id):
    gens = General.objects.annotate(
        amt=Cast("total_amount_expended", output_field=BigIntegerField())
    ).filter(Q(auditee_ein=ein), Q(report_id=report_id), Q(audit_year="2019"))

    if len(gens) != 1:
        return (len(gens), 0)
    gen = gens[0]
    return (1, gen.amt)


def get_2019_cfdas(ein, report_id):
    cfdas = FederalAward.objects.annotate(
        amt=Cast("amount_expended", output_field=BigIntegerField())
    ).filter(Q(report_id=report_id))

    if len(cfdas) == 0:
        return None
    baseline_cfdas = []
    for row in cfdas:
        baseline_cfdas.append((row.federal_agency_prefix, row.amt, row.is_direct))
    return baseline_cfdas


def calc_cfda_amounts(cfdas):
    total_amount_agency = defaultdict(lambda: 0)
    total_da_amount_agency = defaultdict(lambda: 0)
    for cfda in cfdas:
        agency = cfda[0][:2]
        amount = cfda[1] or 0
        direct = cfda[2]
        total_amount_agency[agency] += amount
        if direct == "Y":
            total_da_amount_agency[agency] += amount
    return (
        prune_dict_to_max_values(total_amount_agency),
        prune_dict_to_max_values(total_da_amount_agency),
    )


def prune_dict_to_max_values(data: dict):
    """
    prune_dict_to_max_values({"a": 5, "b": 10, "c": 10}) => {"b": 10, "c": 10}
    """
    if len(data) == 0:
        return data

    pruned_dict = {}
    max_value = max(data.values())
    for key, value in data.items():
        if value == max_value:
            pruned_dict[key] = value

    return pruned_dict


def record_cog_assignment(report_id, user, cognizant_agency):
    """
    To be unvoked by app to persist the computed cog agency
    """
    CognizantAssignment(
        report_id=report_id,
        cognizant_agency=cognizant_agency,
        assignor_email=user.email,
    ).save()
