from collections import defaultdict
from .models import SingleAuditChecklist, CognizantBaseline
from census2019.models import Cfda19, Gen19

COG_LIMIT = 50_000_000
DA_THRESHOLD_FACTOR = 0.0


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
        return max_da_agency.keys()[0]
    return max_total_agency.keys()[0]


def determine_2019_agency(ein):
    cognizant_agency = CognizantBaseline.objects.get(
        audit_year=2019,
        ein=ein,
    ).cognizant_agency
    return cognizant_agency


def set_2019_baseline():
    gens = Gen19.objects.filter(aufityear=2019, amount__ge=COG_LIMIT)
    for gen in gens:
        ein = gen.ein
        total_amount_expended = gen.amount
        cfdas = Cfda19.objects.filter(aufityear=2019, dbkey=gen.dbkey)
        (total_da_amount_expended, max_total_agency, max_da_agency) = calc_cfda_amounts(
            cfdas
        )
        cognizant_agency = determine_agency(
            total_amount_expended,
            total_da_amount_expended,
            max_total_agency,
            max_da_agency,
        )
        CognizantBaseline(
            audit_year=2019, ein=ein, cognizant_agency=cognizant_agency
        ).save()


def calc_cfda_amounts(cfdas):
    # TODO Are we mapping the corect fields?
    total_amount_agency = defaultdict(lambda: 0)
    total_da_amount_agency = defaultdict(lambda: 0)
    total_da_amount_expended = 0
    for cfda in cfdas:
        agency = cfda.cfda
        total_amount_agency[agency] += cfda.amount
        if cfda.direct == "Y":
            total_da_amount_expended += cfda.programtotal
            total_da_amount_agency[agency] += cfda.programtotal
    max_total_agency, max_da_agency = _extract_max_agency(
        total_amount_agency, total_da_amount_agency
    )
    return total_da_amount_expended, max_total_agency, max_da_agency


def _extract_max_agency(total_amount_agency, total_da_amount_agency):
    max_total_agency = max(total_amount_agency.items(), key=lambda x: x[1])
    max_da_agency = max(total_da_amount_agency.items(), key=lambda x: x[1])
    return max_total_agency, max_da_agency
