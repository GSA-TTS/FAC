import requests
import os
import time
from pprint import pprint
import math
import json

URI = "http://localhost:3000"

# GET {{scheme}}://{{apiUrl}}/general?report_id=eq.2021-12-CENSUS-0000250449
# authorization: {{authorization}}
# x-api-user-id: {{xApiUserId}}
# accept-profile: public_api_v1_0_0
# Accept: application/vnd.pgrst.plan


def fetch_fa_exp(api_version):
    total_cost = 0
    for offset in range(0, 4000000, 20000):
        print(f"fetch_fa_exp api {api_version} offset {offset}")
        query = f"{URI}/federal_awards?limit=20000&offset={offset}"
        headers = {
            "accept-profile": api_version,
            "accept": "application/vnd.pgrst.plan+json",
            "x-api-user-id": os.getenv("API_KEY_ID"),
            "authorization": f"bearer {os.getenv('CYPRESS_API_GOV_JWT')}",
        }

        resp = requests.get(query, headers=headers)
        # We get back a list of one plan, and we want the total cost.
        total_cost += resp.json()[0]["Plan"]["Total Cost"]
    return math.floor(total_cost)


def fetch_fa_by_year_exp(api_version):
    total_cost = 0
    for year in range(16, 24):
        audit_year = f"20{year:02}"
        for offset in range(0, 1000000, 20000):
            print(
                f"fetch_fa_by_year_exp api {api_version} ay {audit_year} offset {offset}"
            )
            query = f"{URI}/federal_awards?audit_year=eq.{audit_year}&limit=20000&offset={offset}"
            headers = {
                "accept-profile": api_version,
                "accept": "application/vnd.pgrst.plan+json",
                "x-api-user-id": os.getenv("API_KEY_ID"),
                "authorization": f"bearer {os.getenv('CYPRESS_API_GOV_JWT')}",
            }

            resp = requests.get(query, headers=headers)
            # We get back a list of one plan, and we want the total cost.
            total_cost += resp.json()[0]["Plan"]["Total Cost"]
    return math.floor(total_cost)


def fetch_fa_time(api_version):
    total_cost = 0
    for offset in range(0, 4000000, 20000):
        query = f"{URI}/federal_awards?limit=20000&offset={offset}"
        headers = {
            "accept-profile": api_version,
            "x-api-user-id": os.getenv("API_KEY_ID"),
            "authorization": f"bearer {os.getenv('CYPRESS_API_GOV_JWT')}",
        }
        t0 = time.time()
        resp = requests.get(query, headers=headers)
        t1 = time.time()
        # We get back a list of one plan, and we want the total cost.
        total_cost += t1 - t0
        print(f"fetch_fa_time api {api_version} offset {offset} time {t1-t0}")
    return math.floor(total_cost)


def fetch_fa_time_by_year(api_version):
    total_cost = 0
    for year in range(16, 24):
        for offset in range(0, 1000000, 20000):
            audit_year = f"20{year:02}"
            query = f"{URI}/federal_awards?audit_year=eq.{audit_year}&limit=20000&offset={offset}"
            headers = {
                "accept-profile": api_version,
                "x-api-user-id": os.getenv("API_KEY_ID"),
                "authorization": f"bearer {os.getenv('CYPRESS_API_GOV_JWT')}",
            }
            t0 = time.time()
            resp = requests.get(query, headers=headers)
            t1 = time.time()
            # We get back a list of one plan, and we want the total cost.
            total_cost += t1 - t0
            print(
                f"fetch_fa_time_by_year api {api_version} ay {audit_year} offset {offset} time {t1-t0}"
            )
    return math.floor(total_cost)


def fetch_fa_batches_exp():
    total_cost = 0
    for batch_no in range(0, 235):
        query = f"{URI}/federal_awards?batch_number=eq.{batch_no}"
        headers = {
            "accept-profile": "public_api_v1_0_0",
            "accept": "application/vnd.pgrst.plan+json",
            "x-api-user-id": os.getenv("API_KEY_ID"),
            "authorization": f"bearer {os.getenv('CYPRESS_API_GOV_JWT')}",
        }

        resp = requests.get(query, headers=headers)
        # We get back a list of one plan, and we want the total cost.
        total_cost += resp.json()[0]["Plan"]["Total Cost"]
    return math.floor(total_cost)


def fetch_fa_batches_time():
    total_cost = 0
    for batch_no in range(0, 235):
        print(f"batch number: {batch_no}")
        query = f"{URI}/federal_awards?batch_number=eq.{batch_no}"
        headers = {
            "accept-profile": "public_api_v1_0_0",
            "x-api-user-id": os.getenv("API_KEY_ID"),
            "authorization": f"bearer {os.getenv('CYPRESS_API_GOV_JWT')}",
        }
        t0 = time.time()
        resp = requests.get(query, headers=headers)
        t1 = time.time()
        # We get back a list of one plan, and we want the total cost.
        total_cost += t1 - t0
    return math.floor(total_cost)


def make_ratios(d1, d2):
    min = math.inf
    for k, v in d1.items():
        if v < min:
            min = v
    for k, v in d1.items():
        d2[k] = round(v / min, 2)


if __name__ == "__main__":
    results1 = {}
    results2 = {}
    results3 = {}
    results4 = {}

    results1["api110_by_year"] = fetch_fa_by_year_exp("api_v1_1_0")
    results1["ap110"] = fetch_fa_exp("api_v1_1_0")
    results1["public100"] = fetch_fa_exp("public_api_v1_0_0")
    results1["public100_batches"] = fetch_fa_batches_exp()
    results1["public100_by_year"] = fetch_fa_by_year_exp("public_api_v1_0_0")

    print("Running timing tests... ~5m")

    results3["public100_by_year"] = fetch_fa_time_by_year("public_api_v1_0_0")
    results3["public100"] = fetch_fa_time("public_api_v1_0_0")
    results3["public100_batches"] = fetch_fa_batches_time()
    results3["ap110"] = fetch_fa_time("api_v1_1_0")
    results3["ap110_by_year"] = fetch_fa_time_by_year("api_v1_1_0")

    make_ratios(results1, results2)
    make_ratios(results3, results4)
    results1["desc"] = "EXPLAIN raw"
    results2["desc"] = "EXPLAIN ratio"
    results3["desc"] = "TIME raw"
    results4["desc"] = "TIME ratio"
    # results1 is the raw EXPLAIN cost of downloading all of federal_awards
    pprint(results1)
    # results2 is the ratio
    pprint(results2)
    # results3 is the raw timing
    pprint(results3)
    # results4 is the ratio for timings
    pprint(results4)

# Where there is no index on the audit_year column.
# by_year is worse.
# {'ap110': 36737858,
#  'api110_by_year': 87880072,
#  'public100': 36305424,
#  'public100_batches': 1176467,
#  'public100_by_year': 11407901}
# {'ap110': 31,
#  'api110_by_year': 74,
#  'public100': 30,
#  'public100_batches': 1,
#  'public100_by_year': 9}
# {'ap110': 188,
#  'ap110_by_year': 304,
#  'public100': 62,
#  'public100_batches': 29,
#  'public100_by_year': 40}
# {'ap110': 6,
#  'ap110_by_year': 10,
#  'public100': 2,
#  'public100_batches': 1,
#  'public100_by_year': 1}


# {'ap110': 36737858,
#  'api110_by_year': 87880072,
#  'desc': 'EXPLAIN raw',
#  'public100': 36304899,
#  'public100_batches': 1179458,
#  'public100_by_year': 11407650}
# {'ap110': 31.15,
#  'api110_by_year': 74.51,
#  'desc': 'EXPLAIN ratio',
#  'public100': 30.78,
#  'public100_batches': 1.0,
#  'public100_by_year': 9.67}
# {'ap110': 193,
#  'ap110_by_year': 312,
#  'desc': 'TIME raw',
#  'public100': 63,
#  'public100_batches': 29,
#  'public100_by_year': 45}
# {'ap110': 6.66,
#  'ap110_by_year': 10.76,
#  'desc': 'TIME ratio',
#  'public100': 2.17,
#  'public100_batches': 1.0,
#  'public100_by_year': 1.55}
