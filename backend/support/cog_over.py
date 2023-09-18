from collections import defaultdict
from .models import CognizantBaseline, CognizantAssignment
from dissemination.models import General
from dissemination.hist_models.census_2019 import CensusGen19, CensusCfda19
from dissemination.hist_models.census_2022 import CensusGen22
from django.db.models.functions import Cast
from django.db.models import BigIntegerField, Q

import logging

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
    dbkey = get_dbkey(ein, uei)

    cog_agency = lookup_baseline(ein, uei, dbkey)
    if cog_agency:
        return cog_agency
    (gen_count, total_amount_expended) = get_2019_gen(ein, dbkey)
    if gen_count != 1:
        return None
    cfdas = get_2019_cfdas(ein, dbkey)
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


def get_dbkey(ein, uei):
    try:
        dbkey = CensusGen22.objects.values_list("dbkey", flat=True).get(
            Q(ein=ein), Q(uei=uei) | Q(uei=None)
        )[:]
    except (CensusGen22.DoesNotExist, CensusGen22.MultipleObjectsReturned):
        dbkey = None
    return dbkey


def lookup_baseline(ein, uei, dbkey):
    try:
        cognizant_agency = CognizantBaseline.objects.values_list(
            "cognizant_agency", flat=True
        ).get(Q(is_active=True) & ((Q(ein=ein) & Q(dbkey=dbkey)) | Q(uei=uei)))[:]
    except (CognizantBaseline.DoesNotExist, CognizantBaseline.MultipleObjectsReturned):
        cognizant_agency = None
    return cognizant_agency


def get_2019_gen(ein, dbkey):
    gens = CensusGen19.objects.annotate(
        amt=Cast("totfedexpend", output_field=BigIntegerField())
    ).filter(Q(ein=ein), Q(dbkey=dbkey) | Q(dbkey=None))

    if len(gens) != 1:
        return (len(gens), 0)
    gen = gens[0]
    return (1, gen.amt)


def get_2019_cfdas(ein, dbkey):
    cfdas = CensusCfda19.objects.annotate(
        amt=Cast("amount", output_field=BigIntegerField())
    ).filter(Q(ein=ein), Q(dbkey=dbkey) | Q(dbkey=None))

    if len(cfdas) == 0:
        return None
    baseline_cfdas = []
    for row in cfdas:
        baseline_cfdas.append((row.cfda, row.amt, row.direct))
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


def prune_dict_to_max_values(dict):
    if len(dict) == 0:
        return dict

    pruned_dict = {}
    max_value = max(dict.values())
    for key, value in dict.items():
        if value == max_value:
            pruned_dict[key] = value

    return pruned_dict


def propogate_cog_update(cog_assignment: CognizantAssignment):
    """
    Invoked after a row is inserted into CognizantAssignment
    """
    (sac, cognizant_agency) = (cog_assignment.sac, cog_assignment.cognizant_agency)
    sac.cognizant_agency = cognizant_agency
    sac.save()

    (ein, uei) = (sac.auditee_uei, sac.ein)
    cbs = CognizantBaseline.objects.filter(Q(ein=ein) | Q(uei=uei))
    for cb in cbs:
        cb.is_active = False
        cb.save()
    CognizantBaseline(ein=ein, uei=uei, cognizant_agency=cognizant_agency).save()

    try:
        gen = General.objects.get(report_id=sac.report_id)
        gen.cognizant_agency = cognizant_agency
        gen.save()
    except General.DoesNotExist:
        pass  # etl may not have been run yet


def record_cog_assignment(report_id, user, cognizant_agency):
    """
    To be unvoked by app to persist the computed cog agency
    """
    CognizantAssignment(
        report_id=report_id,
        cognizant_agency=cognizant_agency,
        assignor_email=user.email,
    ).save()


def assign_cog_over(sac):
    """
    Function that the FAC app uses when a submission is completed and cog_over needs to be assigned.
    """
    # (conizantg_agency, oversight_agency) = compute_cog_over(sac)
    conizantg_agency, oversight_agency = compute_cog_over(
        sac.federal_awards, sac.submission_status, sac.ein, sac.auditee_uei
    )
    if oversight_agency:
        sac.oversight_agency = oversight_agency
        sac.save()
        return
    if conizantg_agency:
        record_cog_assignment(sac.report_id, sac.submitted_by, conizantg_agency)
