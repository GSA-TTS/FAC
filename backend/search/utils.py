import json
import os
import requests


# Reference initial results from federal award,
# make new request to auditee, and add important info.
def cross_reference_federal_award(initial_results):
    API_KEY = os.getenv("API_GOV_KEY")
    SEARCH_URL = os.getenv("API_GOV_URL")

    cross_search_path = "vw_auditee"
    cross_search_params = {"limit": 100, "api_key": API_KEY}
    cross_id_list = []
    for x in initial_results:
        if x.get("cpa_ein"):
            cross_id_list.append(x["cpa_ein"])
    temp = "cd.{"
    for y in cross_id_list:
        temp += str(y) + ","
    temp = temp[:-1]
    temp += "}"
    cross_search_params["ein_list"] = str(temp)
    cross_response = requests.get(
        SEARCH_URL + cross_search_path, params=cross_search_params, timeout=10
    )
    cross_results = json.loads(cross_response.text)
    for x in initial_results:
        for y in cross_results:
            if x.get("cpa_ein") == y.get("ein_list")[0]:
                x["uei_list"] = y.get("uei_list")
                x["auditee_name"] = y.get("auditee_name")
                x["auditee_city"] = y.get("auditee_city")
                x["auditee_state"] = y.get("auditee_state")
                x["duns_list"] = y.get("duns_list")

    return initial_results


# Reference initial results from general,
# make new request to auditee, and add important info.
def cross_reference_general(initial_results):
    API_KEY = os.getenv("API_GOV_KEY")
    SEARCH_URL = os.getenv("API_GOV_URL")

    cross_search_path = "vw_auditee"
    cross_search_params = {"limit": 100, "api_key": API_KEY}
    cross_id_list = []
    for x in initial_results:
        if x.get("auditee_id"):
            cross_id_list.append(x["auditee_id"])
    temp = "in.("
    for y in cross_id_list:
        temp += str(y) + ","
    temp = temp[:-1]
    temp += ")"
    cross_search_params["id"] = str(temp)
    cross_response = requests.get(
        SEARCH_URL + cross_search_path, params=cross_search_params, timeout=10
    )
    cross_results = json.loads(cross_response.text)
    for x in initial_results:
        for y in cross_results:
            if x.get("auditee_id") == y.get("id"):
                x["uei_list"] = y.get("uei_list")
                x["auditee_city"] = y.get("auditee_city")
                x["auditee_state"] = y.get("auditee_state")
                x["duns_list"] = y.get("duns_list")

    return initial_results
