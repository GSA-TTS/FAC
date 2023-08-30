from collections import defaultdict
from .models import SingleAuditChecklist
from dissemination.models import CensusGen19, CensusCfda19
from django.db.models.functions import Cast
from django.db.models import BigIntegerField


COG_LIMIT = 50_000_000
DA_THRESHOLD_FACTOR = 0.25


def cog_over(sac: SingleAuditChecklist):
    awards = sac.federal_awards["FederalAwards"]
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
        print("Assigning an oversight agenct", oversight_agency)
        return (cognizant_agency, oversight_agency)
    cognizant_agency = determine_2019_agency(sac.ein)
    if cognizant_agency:
        print("Assigning a 2019 cog agency", cognizant_agency)
        return (cognizant_agency, oversight_agency)
    cognizant_agency = agency
    print(" Assigning a current cog agenct", cognizant_agency)
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
    tie_breaker = {}
    for key, value in max_da_agency.items():
        if value >= DA_THRESHOLD_FACTOR * total_amount_expended:
            tie_breaker[key] = value + max_total_agency[key]
    for agency in prune_dict_to_max_values(tie_breaker).keys():
        return agency
    for agency in max_total_agency.keys():
        return agency


def determine_2019_agency(ein):
    (dbkey, total_amount_expended) = get_baseline_gen(ein)
    if not dbkey:
        return None
    cfdas = get_baseline_cfdas(dbkey)
    if not cfdas:
        return None
    (max_total_agency, max_da_agency) = calc_cfda_amounts(cfdas)
    cognizant_agency = determine_agency(
        total_amount_expended,
        max_total_agency,
        max_da_agency,
    )
    return cognizant_agency


def get_baseline_gen(ein):
    gens = CensusGen19.objects.annotate(
        amt=Cast("totfedexpend", output_field=BigIntegerField())
    ).filter(ein=ein)
    print(f"Found {len(gens)} gen in 2019 for ein:{ein}")
    if len(gens) != 1:
        return (None, 0)
    gen = gens[0]
    return (gen.dbkey, gen.amt)


def get_baseline_cfdas(dbkey):
    cfdas = CensusCfda19.objects.annotate(
        amt=Cast("amount", output_field=BigIntegerField())
    ).filter(dbkey=dbkey)
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
