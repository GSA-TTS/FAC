from collections import defaultdict
import logging
import math

from django.db.models.functions import Cast
from django.db.models import BigIntegerField, Q

from support.models import CognizantAssignment
from dissemination.models import General, MigrationInspectionRecord, FederalAward

logger = logging.getLogger(__name__)


COG_LIMIT = 50_000_000
DA_THRESHOLD_FACTOR = 0.25

FIRST_BASELINE_YEAR = 2019
BASELINE_VALID_FOR_YEARS = 5

DBKEY_TO_UEI_TRANSITION_YEAR = "2022"


def compute_cog_over(
    federal_awards, submission_status, auditee_ein, auditee_uei, audit_year
):
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

    cognizant_agency = determine_hist_agency(auditee_ein, auditee_uei, audit_year)
    if cognizant_agency:
        return (cognizant_agency, oversight_agency)
    cognizant_agency = agency
    return (cognizant_agency, oversight_agency)


def calc_base_year(audit_year):
    # Note: 2019 is the first supported baseline year in GSAFAC
    # For audit years 2019 through 2023, baseline year is 2019
    # For audit years 2024 through 2028, baseline year is 2024
    # For audit years 2029 through 2033, baseline year is 2029
    # For audit years 2034 through 2038, baseline year is 2034
    # and so on
    base_year = (
        math.floor((int(audit_year) - FIRST_BASELINE_YEAR) / BASELINE_VALID_FOR_YEARS)
        * BASELINE_VALID_FOR_YEARS
    ) + FIRST_BASELINE_YEAR
    return str(base_year)


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


def determine_hist_agency(ein, uei, audit_year):
    base_year = calc_base_year(audit_year)
    dbkey = None
    if int(base_year) == FIRST_BASELINE_YEAR:
        dbkey = get_dbkey(ein, uei)

    cog_agency = lookup_latest_cog(ein, uei, dbkey, base_year, audit_year)
    if cog_agency:
        return cog_agency

    (gen_count, total_amount_expended, report_id_base_year) = get_base_gen(
        ein, uei, base_year
    )
    if gen_count != 1:
        return None
    cfdas = get_base_cfdas(report_id_base_year)
    if not cfdas:
        return None
    (max_total_agency, max_da_agency) = calc_cfda_amounts(cfdas)
    cognizant_agency = determine_agency(
        total_amount_expended,
        max_total_agency,
        max_da_agency,
    )
    return cognizant_agency


def get_dbkey(ein, uei):
    try:
        report_id = General.objects.values_list("report_id", flat=True).get(
            Q(auditee_ein=ein),
            Q(auditee_uei=uei),
            Q(audit_year=DBKEY_TO_UEI_TRANSITION_YEAR),
        )
    except (General.DoesNotExist, General.MultipleObjectsReturned):
        report_id = None
        dbkey = None
        return dbkey

    try:
        dbkey = MigrationInspectionRecord.objects.values_list("dbkey", flat=True).get(
            Q(report_id=report_id), Q(audit_year=DBKEY_TO_UEI_TRANSITION_YEAR)
        )
    except (
        MigrationInspectionRecord.DoesNotExist,
        MigrationInspectionRecord.MultipleObjectsReturned,
    ):
        dbkey = None
    return dbkey


def lookup_latest_cog(ein, uei, dbkey, base_year, audit_year):
    # Note: In Census historical data,
    #       From 2016 through 2022, (dbkey, ein) is the identifier for audits through 2021.
    #       In 2022, entities transitioned from dbkey to uei.  2022 data contains dbkey, ein and uei.
    #       From 2022 on, (ein, uei) is the identifier for audits.
    query_years = [str(year) for year in range(int(base_year), int(audit_year) + 1)]
    cognizant_agency = None

    first_base_year_query_section = (
        Q(auditee_ein=ein)
        & Q(report_id__icontains=dbkey)
        & Q(report_id__icontains="CENSUS")
    )
    other_year_query_section = Q(auditee_ein=ein) & Q(auditee_uei=uei)

    query_subsection = other_year_query_section
    if (int(base_year) == FIRST_BASELINE_YEAR) and (dbkey is not None):
        query_subsection = first_base_year_query_section

    try:
        cognizant_agency = (
            General.objects.filter(Q(audit_year__in=query_years) & (query_subsection))
            .exclude(cognizant_agency__isnull=True)
            .exclude(cognizant_agency__exact="")
            .order_by("-audit_year")
            .values_list("cognizant_agency", flat=True)[:]
        )
        if len(cognizant_agency) >= 1:
            return cognizant_agency[0]
    except General.DoesNotExist:
        cognizant_agency = None
    return cognizant_agency


def get_base_gen(ein, uei, base_year):
    gens = General.objects.annotate(
        amt=Cast("total_amount_expended", output_field=BigIntegerField())
    ).filter(Q(auditee_ein=ein), Q(auditee_uei=uei), Q(audit_year=base_year))

    if len(gens) != 1:
        return (len(gens), 0, None)
    gen = gens[0]
    return (1, gen.amt, gen.report_id)


def get_base_cfdas(report_id):
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
