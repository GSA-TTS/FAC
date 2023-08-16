from collections import defaultdict
import os
from .models import SingleAuditChecklist, CognizantBaseline
import sqlalchemy


COG_LIMIT = 50_000_000
DA_THRESHOLD_FACTOR = 0.25


def cog_over(sac: SingleAuditChecklist):
    awards = sac.federal_awards["FederalAwards"]
    total_amount_expended = awards.get("total_amount_expended")
    cognizant_agency = oversight_agency = None
    (total_da_amount_expended, max_total_agency, max_da_agency) = calc_award_amounts(
        awards
    )

    # print("\n\ntotal_amount_expended =", total_amount_expended)
    # print("total_da_amount_expended = ", total_da_amount_expended)
    # print("max_total_agency = ", max_total_agency)
    # print("max_da_agency = ", max_da_agency)

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
        # print("max_da_agency[0] = ", max_da_agency[0])
        return max_da_agency[0]
    # print("max_total_agency[0] = ", max_total_agency[0])
    return max_total_agency[0]


def determine_2019_agency(ein):
    try:
        cognizant_agency = CognizantBaseline.objects.get(
            audit_year=2019,
            ein=ein,
        ).cognizant_agency
        return cognizant_agency
    except CognizantBaseline.DoesNotExist:
        return None


def set_2019_baseline():
    engine = sqlalchemy.create_engine(
        os.getenv("DATABASE_URL").replace("postgres", "postgresql", 1)
    )
    session = sqlalchemy.orm.Session(engine)
    gen_table = sqlalchemy.Table("census_gen19", session.get_bind())
    cfda_table = sqlalchemy.Table("census_cfda19", session.get_bind())

    gens = (
        session.query(gen_table)
        .filter(gen_table.c.aufityear == 2019)
        .filter(gen_table.c.amount >= COG_LIMIT)
        .all()
    )

    for gen in gens:
        dbkey = gen.dbkey
        ein = gen.ein
        total_amount_expended = gen.amount
        cfdas = (
            session.query(cfda_table)
            .filter(cfda_table.c.aufityear == 2019)
            .filter(cfda_table.c.dbkey == gen.dbkey)
            .all()
        )
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
            dbkey=dbkey, audit_year=2019, ein=ein, cognizant_agency=cognizant_agency
        ).save()


def calc_cfda_amounts(cfdas):
    total_amount_agency = defaultdict(lambda: 0)
    total_da_amount_agency = defaultdict(lambda: 0)
    total_da_amount_expended = 0
    for cfda in cfdas:
        agency = cfda.cfda
        total_amount_agency[agency] += cfda.program["amount_expended"]
        if cfda.direct == "Y":
            total_da_amount_expended += cfda.program["amount_expended"]
            total_da_amount_agency[agency] += cfda.program["amount_expended"]
    max_total_agency, max_da_agency = _extract_max_agency(
        total_amount_agency, total_da_amount_agency
    )
    return total_da_amount_expended, max_total_agency, max_da_agency


def _extract_max_agency(total_amount_agency, total_da_amount_agency):
    max_total_agency = max(total_amount_agency.items(), key=lambda x: x[1])
    max_da_agency = max(total_da_amount_agency.items(), key=lambda x: x[1])
    return max_total_agency, max_da_agency
