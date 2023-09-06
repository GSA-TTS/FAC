from collections import defaultdict
import os
from .models import SingleAuditChecklist, CognizantBaseline
from dissemination.models import CensusGen22, cognizant_agencies_2021_2025, CensusGen19, CensusCfda19
from django.db.models.functions import Cast
from django.db.models import BigIntegerField
import sqlalchemy


COG_LIMIT = 50_000_000
DA_THRESHOLD_FACTOR = 0.25
REF_YEAR = "2019"


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

    # Find dbkey from Gen22 table
    dbkey = find_dbkey_from_Gen22(sac.auditee_ein, sac.auditee_uei)
    if dbkey:
        # Check cognizant_agencies_21_25 table
        cognizant_agency = check_21_25_cog_assignment(dbkey, sac.auditee_ein)
        if cognizant_agency:
            return (cognizant_agency, oversight_agency)
        cognizant_agency = determine_2019_agency_w_dbkey(sac.auditee_ein, dbkey)
        if cognizant_agency:
            return (cognizant_agency, oversight_agency)
    cognizant_agency = agency
    return (cognizant_agency, oversight_agency)


def find_dbkey_from_Gen22(ein, uei):
    dbkey = CensusGen22.objects.annotate(
        int_ein=Cast("ein", output_field=BigIntegerField())
        ).filter(int_ein=int(ein), uei=uei).values_list("dbkey", flat=True)
    if len(dbkey) > 0:
        return dbkey[0]
    return None


def check_21_25_cog_assignment(dbkey, ein):
    cog_agency_list = cognizant_agencies_2021_2025.objects.annotate(
        int_ein=Cast("ein", output_field=BigIntegerField())
        ).filter(dbkey=dbkey, int_ein=int(ein)).values_list("cogagency", flat=True)
    if len(cog_agency_list) > 0:
        return cog_agency_list[0]
    return None


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
        if max_da_agency[1] >= DA_THRESHOLD_FACTOR * total_amount_expended:
            return max_da_agency[0]
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
    except CognizantBaseline.MultipleObjectsReturned:
        print("Multiple objects detected for ein = ", ein)
        return None


def determine_2019_agency_w_dbkey(ein, dbkey):
    try:
        cognizant_agency = CognizantBaseline.objects.get(
            audit_year=2019,
            ein=ein,
            dbkey=dbkey,
        ).cognizant_agency
        return cognizant_agency
    except CognizantBaseline.DoesNotExist:
        return None
    except CognizantBaseline.MultipleObjectsReturned:
        print("Multiple objects detected for ein = ", ein)
        return None


def set_2019_baseline():
    engine = sqlalchemy.create_engine(
        os.getenv("DATABASE_URL").replace("postgres", "postgresql", 1)
    )
    # AUDIT_QUERY = """
    #     SELECT gen."DBKEY", gen."EIN", cast(gen."TOTFEDEXPEND" as BIGINT),
    #             cfda."CFDA", cast(cfda."AMOUNT" as BIGINT), cfda."DIRECT", cast(cfda."PROGRAMTOTAL" as BIGINT)
    #     FROM census_gen19 gen, census_cfda19 cfda
    #     WHERE gen."AUDITYEAR" = :ref_year
    #     AND cast(gen."TOTFEDEXPEND" as BIGINT) > :threshold
    #     AND gen."DBKEY" = cfda."DBKEY"
    #     AND gen."EIN" = cfda."EIN"
    #     ORDER BY gen."DBKEY"
    # """
    AUDIT_QUERY = """
        SELECT gen."DBKEY", gen."EIN", cast(gen."TOTFEDEXPEND" as BIGINT),
                cfda."CFDA", cast(cfda."AMOUNT" as BIGINT), cfda."DIRECT"
        FROM census_gen19 gen, census_cfda19 cfda
        WHERE gen."AUDITYEAR" = :ref_year
        AND gen."DBKEY" = cfda."DBKEY"
        AND gen."EIN" = cfda."EIN"
        ORDER BY gen."DBKEY"
    """
    with engine.connect() as conn:
        result = conn.execute(
            sqlalchemy.text(AUDIT_QUERY), {"ref_year": REF_YEAR}
        )
        gens = []
        cfdas = []

        for row in result:
            (DBKEY, EIN, TOTFEDEXPEND, CFDA, AMOUNT, DIRECT) = row
            if (DBKEY, EIN, TOTFEDEXPEND) not in gens:
                gens.append((DBKEY, EIN, TOTFEDEXPEND))
            if (DBKEY, CFDA, AMOUNT, DIRECT, EIN) not in cfdas:
                cfdas.append((DBKEY, CFDA, AMOUNT, DIRECT, EIN))

    CognizantBaseline.objects.all().delete()
    for gen in gens:
        dbkey = gen[0]
        ein = gen[1]
        total_amount_expended = gen[2]
        (total_da_amount_expended, max_total_agency, max_da_agency) = calc_cfda_amounts(
            cfdas=[cfda for cfda in cfdas if ((cfda[0] == dbkey) & (cfda[4] == ein))]
        )
        cognizant_agency = determine_agency(
            total_amount_expended,
            total_da_amount_expended,
            max_total_agency,
            max_da_agency,
        )
        if cognizant_agency:
            CognizantBaseline(
                dbkey=dbkey, audit_year=2019, ein=ein, cognizant_agency=cognizant_agency
            ).save()
    return CognizantBaseline.objects.count()


def calc_cfda_amounts(cfdas):
    total_amount_agency = defaultdict(lambda: 0)
    total_da_amount_agency = defaultdict(lambda: 0)
    total_da_amount_expended = 0
    for cfda in cfdas:
        agency = cfda[1][:2]
        amount = cfda[2] or 0
        direct = cfda[3]
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
