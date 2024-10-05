import requests
import os
import time
from pprint import pprint
import math

URI = "http://localhost:3000"

# GET {{scheme}}://{{apiUrl}}/general?report_id=eq.2021-12-CENSUS-0000250449
# authorization: {{authorization}}
# x-api-user-id: {{xApiUserId}}
# accept-profile: public_api_v1_0_0
# Accept: application/vnd.pgrst.plan


def fetch_fa_exp(api_version):
    total_cost = 0
    for offset in range(0, 4000000, 20000):
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


def fetch_fa_time(api_version):
    total_cost = 0
    for offset in range(0, 4000000, 20000):
        print(f"api {api_version} offset {offset}")
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


if __name__ == "__main__":
    results1 = {}
    results2 = {}
    results3 = {}
    results4 = {}

    results1["ap110"] = fetch_fa_exp("api_v1_1_0")
    results1["public200"] = fetch_fa_exp("public_api_v1_0_0")
    results1["public200_batches"] = fetch_fa_batches_exp()

    min = math.inf
    for k, v in results1.items():
        if v < min:
            min = v
    for k, v in results1.items():
        results2[k] = math.floor(v / min)

    print("Running timing tests... ~5m")

    results3["ap110"] = fetch_fa_time("api_v1_1_0")
    results3["public200"] = fetch_fa_time("public_api_v1_0_0")
    results3["public200_batches"] = fetch_fa_batches_time()

    min = math.inf
    for k, v in results3.items():
        if v < min:
            min = v
    for k, v in results3.items():
        results4[k] = math.floor(v / min)

    # results1 is the raw EXPLAIN cost of downloading all of federal_awards
    pprint(results1)
    # results2 is the ratio
    pprint(results2)
    # results3 is the raw timing
    pprint(results3)
    # results4 is the ratio for timings
    pprint(results4)
