from collections import defaultdict
from .models import SingleAuditChecklist
from dissemination.models import CensusGen19, CensusCfda19


COG_LIMIT = 50_000_000
DA_THRESHOLD_FACTOR = 0.25


def cog_over(sac: SingleAuditChecklist):
    awards = sac.federal_awards["FederalAwards"]
    total_amount_expended = awards.get("total_amount_expended")
    cognizant_agency = oversight_agency = None
    (total_da_amount_expended, max_total_agency, max_da_agency) = calc_award_amounts(
        awards
    )

    agency = determine_agency(
        total_amount_expended,
        total_da_amount_expended,
        max_total_agency,
        max_da_agency,
    )

    if total_amount_expended <= COG_LIMIT:
        oversight_agency = agency
        return (cognizant_agency, oversight_agency)
    cognizant_agency = determine_2019_agency(sac.ein)
    if cognizant_agency:
        return (cognizant_agency, oversight_agency)
    cognizant_agency = agency
    return (cognizant_agency, oversight_agency)


def calc_award_amounts(awards):
    total_amount_agency = defaultdict(lambda: 0)
    total_da_amount_agency = defaultdict(lambda: 0)
    total_da_amount_expended = 0
    for award in awards["federal_awards"]:
        agency = award["program"]["federal_agency_prefix"]
        total_amount_agency[agency] += award["program"]["amount_expended"]
        if award["direct_or_indirect_award"]["is_direct"] == "Y":
            total_da_amount_expended += award["program"]["amount_expended"]
            total_da_amount_agency[agency] += award["program"]["amount_expended"]
    max_total_agency, max_da_agency = _extract_max_agency(
        total_amount_agency, total_da_amount_agency
    )
    return total_da_amount_expended, max_total_agency, max_da_agency


def determine_agency(
    total_amount_expended, total_da_amount_expended, max_total_agency, max_da_agency
):
    if total_da_amount_expended >= DA_THRESHOLD_FACTOR * total_amount_expended:
        return max_da_agency[0]
    return max_total_agency[0]


def determine_2019_agency(ein):
    (dbkey, total_amount_expended) = get_baseline_gen(ein)
    if not dbkey:
        return None
    cfdas = get_baseline_cfdas(dbkey)
    (total_da_amount_expended, max_total_agency, max_da_agency
     ) = calc_cfda_amounts(cfdas)
    cognizant_agency = determine_agency(
            total_amount_expended,
            total_da_amount_expended,
            max_total_agency,
            max_da_agency,
        )
    return cognizant_agency


def get_baseline_gen(ein):
    gens = CensusGen19.objects.filter(ein=ein)
    if len(gens) != 1:
        return (None, 0)
    gen = gens[0]
    return (gen.dbkey, gen.totfedexpend)

def get_baseline_cfdas(dbkey):
    cfdas = CensusCfda19.objects.filter(dbkey=dbkey)    
    baseline_cfdas = []
    for row in cfdas:
        baseline_cfdas.append((row.cfda, row.amount, row.direct))
    return baseline_cfdas


def calc_cfda_amounts(cfdas):
    total_amount_agency = defaultdict(lambda: 0)
    total_da_amount_agency = defaultdict(lambda: 0)
    total_da_amount_expended = 0
    for cfda in cfdas:
        agency = cfda[0][:2]
        amount = cfda[1] or 0
        direct = cfda[2]
        total_amount_agency[agency] += amount
        if direct == "Y":
            total_da_amount_expended += amount
            total_da_amount_agency[agency] += amount
    max_total_agency, max_da_agency = _extract_max_agency(
        total_amount_agency, total_da_amount_agency
    )
    return total_da_amount_expended, max_total_agency, max_da_agency


def _extract_max_agency(total_amount_agency, total_da_amount_agency):
    max_total_agency = max(total_amount_agency.items(), key=lambda x: x[1])
    if len(total_da_amount_agency) > 0:
        max_da_agency = max(total_da_amount_agency.items(), key=lambda x: x[1])
    else:
        max_da_agency = total_da_amount_agency
    return max_total_agency, max_da_agency
