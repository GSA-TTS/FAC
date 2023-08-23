import os
import sqlalchemy
import pandas as pd
from audit.cog_over import calc_cfda_amounts, determine_agency, determine_2019_agency_w_dbkey


COG_LIMIT = 50_000_000
DA_THRESHOLD_FACTOR = 0.25
REF_YEAR = "2022"


def cog_over_for_2022():
    print("Starting cog_over_for_2022.")
    print("DATABASE_URL = ", os.getenv("DATABASE_URL"))

    engine = sqlalchemy.create_engine(
        os.getenv("DATABASE_URL").replace("postgres", "postgresql", 1)
    )
    AUDIT_QUERY = """
        SELECT gen."DBKEY", gen."EIN", cast(gen."TOTFEDEXPEND" as BIGINT),
                gen."COG_OVER", gen."COGAGENCY", gen."OVERSIGHTAGENCY",
                cfda."CFDA", cast(cfda."AMOUNT" as BIGINT), cfda."DIRECT"
        FROM census_gen22 gen, census_cfda22 cfda
        WHERE gen."AUDITYEAR" = :ref_year
        AND cast(gen."TOTFEDEXPEND" as BIGINT) >= :threshold
        AND gen."DBKEY" = cfda."DBKEY"
        ORDER BY gen."DBKEY"
    """
    with engine.connect() as conn:
        result = conn.execute(
            sqlalchemy.text(AUDIT_QUERY), {"ref_year": REF_YEAR, "threshold": COG_LIMIT}
        )
        print("Obtained result from postgres")
        print("result.rowcount = ", result.rowcount)

        gens = []
        cfdas = []
        for row in result:
            (
                DBKEY,
                EIN,
                TOTFEDEXPEND,
                COG_OVER,
                COGAGENCY,
                OVERSIGHTAGENCY,
                CFDA,
                AMOUNT,
                DIRECT,
            ) = row
            if (
                DBKEY,
                EIN,
                TOTFEDEXPEND,
                COG_OVER,
                COGAGENCY,
                OVERSIGHTAGENCY,
            ) not in gens:
                gens.append(
                    (DBKEY, EIN, TOTFEDEXPEND, COG_OVER, COGAGENCY, OVERSIGHTAGENCY)
                )
            if (DBKEY, CFDA, AMOUNT, DIRECT) not in cfdas:
                cfdas.append((DBKEY, CFDA, AMOUNT, DIRECT))

    print("len(gens = ", len(gens))
    print("len(cfdas) = ", len(cfdas))

    # Generate cog / over assignments for 2022
    df_calc = pd.DataFrame(
        columns=["DBKEY", "EIN", "COGOVER", "COGAGENCY", "OVERAGENCY"]
    )
    df_2022 = pd.DataFrame(
        columns=["DBKEY", "EIN", "COGOVER", "COGAGENCY", "OVERAGENCY"]
    )
    df_diff = pd.DataFrame(
        columns=[
            "DBKEY",
            "EIN",
            "COGOVER_CALC",
            "COGAGENCY_CALC",
            "OVERAGENCY_CALC",
            "COGOVER_2022",
            "COGAGENCY_2022",
            "OVERAGENCY_2022",
        ]
    )

    is_match = True
    for gen in gens:
        df_2022_row = {
            "DBKEY": gen[0],
            "EIN": gen[1],
            "COGOVER": gen[3],
            "COGAGENCY": gen[4],
            "OVERAGENCY": gen[5],
        }
        df_2022.loc[len(df_2022)] = df_2022_row

        dbkey = gen[0]
        ein = gen[1]
        total_amount_expended = gen[2]
        (total_da_amount_expended, max_total_agency, max_da_agency) = calc_cfda_amounts(
            cfdas=[cfda for cfda in cfdas if cfda[0] == dbkey]
        )

        agency = determine_agency(
            total_amount_expended,
            total_da_amount_expended,
            max_total_agency,
            max_da_agency,
        )

        oversight_agency = cognizant_agency = None
        if total_amount_expended <= COG_LIMIT:
            oversight_agency = agency
            cogover = "O"
        else:
            cogover = "C"
            cognizant_agency = determine_2019_agency_w_dbkey(ein, dbkey)
            if cognizant_agency is None:
                cognizant_agency = agency

        df_calc_row = {
            "DBKEY": dbkey,
            "EIN": ein,
            "COGOVER": cogover,
            "COGAGENCY": cognizant_agency,
            "OVERAGENCY": oversight_agency,
        }
        df_calc.loc[len(df_calc)] = df_calc_row

        if not (df_calc_row == df_2022_row):
            is_match = False
            df_diff.loc[len(df_diff)] = {
                "DBKEY": dbkey,
                "EIN": ein,
                "COGOVER_CALC": cogover,
                "COGAGENCY_CALC": cognizant_agency,
                "OVERAGENCY_CALC": oversight_agency,
                "COGOVER_2022": gen[3],
                "COGAGENCY_2022": gen[4],
                "OVERAGENCY_2022": gen[5],
            }

    filedir = os.getcwd()
    df_calc.to_csv(os.path.join(filedir, "calc_2022.csv"))
    df_2022.to_csv(os.path.join(filedir, "actual_2022.csv"))
    df_diff.to_csv(os.path.join(filedir, "calc_vs_actual_diff.csv"))

    return (df_calc.shape[0], is_match)
