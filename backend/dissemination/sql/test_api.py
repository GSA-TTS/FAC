#
# Execute as a pytest.
# pytest -s --env local test_api.py
#

import click
import os
import requests
import sys
import uuid


class EnvVars:
    FAC_API_KEY = os.getenv("FAC_API_KEY")
    FAC_API_KEY_ID = os.getenv("CYPRESS_API_GOV_USER_ID")
    FAC_AUTH_BEARER = os.getenv("CYPRESS_API_GOV_JWT")
    RECORDS_REQUESTED = 5


def url(env):
    EnvVars.FAC_API_KEY = os.getenv("FAC_API_KEY")
    match env:
        case "local":
            return "http://localhost:3000"
        case "preview":
            return "https://api-preview.fac.gov"
        case "dev":
            return "https://api-dev.fac.gov"
        case "staging":
            return "https://api-staging.fac.gov"
        case "production":
            return "https://api.fac.gov"
        case _:
            print("No environment provided; exiting.")
            sys.exit()


def headers(env):
    if env in ["local"]:
        if EnvVars.FAC_AUTH_BEARER == None:
            print("FAC_AUTH_BEARER not set.")
            sys.exit()
        if EnvVars.FAC_API_KEY_ID == None:
            print("FAC_API_KEY_ID not set.")
            sys.exit()
        return {
            "authorization": f"bearer {EnvVars.FAC_AUTH_BEARER}",
            "x-api-user-id": EnvVars.FAC_API_KEY_ID,
        }
    elif env in ["preview", "dev", "staging", "production"]:
        if EnvVars.FAC_API_KEY == None:
            print("FAC_API_KEY not set.")
            sys.exit()
        return {
            "x-api-key": EnvVars.FAC_API_KEY,
        }
    else:
        print("No environment matches for header construction.")
        sys.exit()


def api(version):
    return {"accept-profile": version}


def limit(start, end):
    return {"Range-Unit": "items", "Range": f"{start}-{end}"}


# Asserts that an API response is:
# * A list
# * A list composed of objects that all contain the required keys
def good_resp(objs, keys):
    assert isinstance(objs, list)
    assert len(objs) == EnvVars.RECORDS_REQUESTED
    for k in keys:
        for o in objs:
            # print(f"Checking {k} in {o}")
            assert k in o
    return True


# Constructs the base URL for making multiple API calls off of.
def cons(env, api_version):
    def _helper(endpoint, keys):
        base = url(env)
        h = headers(env) | limit(0, EnvVars.RECORDS_REQUESTED - 1) | api(api_version)
        r = requests.get(base + f"/{endpoint}", headers=h)
        # print(r.request.url)
        # print(r.request.headers)
        good_resp(r.json(), keys)

    return _helper


# These tables are common to both the old API and
# the new public data API.
def common_tables(f):
    f("general", ["report_id", "audit_year", "auditee_name"])
    f(
        "federal_awards",
        ["report_id", "amount_expended", "audit_report_type"],
    )
    f("corrective_action_plans", ["report_id", "finding_ref_number", "auditee_uei"])


def test_api_v1_0_3_not_exist(env):
    f = cons(env, "api_v1_0_3")
    try:
        common_tables(f)
        print("This schema/API should not exist.")
        assert False
    except:
        pass


def test_api_v1_1_0(env):
    f = cons(env, "api_v1_1_0")
    common_tables(f)


def test_api_v2_0_0(env):
    f = cons(env, "api_v2_0_0")
    common_tables(f)


def test_suppressed_not_accessible_with_bad_key(env):
    # Stash the token, and wipe it out, so the API
    # calls will fail.
    TEMP_FAC_API_KEY_ID = EnvVars.FAC_API_KEY_ID
    EnvVars.FAC_API_KEY_ID = str(uuid.uuid4())
    f = cons(env, "api_v2_0_0")
    failed_count = 0
    for thunk in [
        lambda: f(
            "suppressed_notes_to_sefa", ["report_id", "content", "is_minimis_rate_used"]
        ),
        lambda: f("suppressed_findings_text", ["report_id", "finding_ref_number"]),
        lambda: f(
            "suppressed_corrective_action_plans",
            ["report_id", "finding_ref_number", "planned_action"],
        ),
    ]:
        try:
            thunk()
        except:
            failed_count += 1
    assert failed_count == 3
    # Restore it in case we need it in later tests.
    EnvVars.FAC_API_KEY_ID = TEMP_FAC_API_KEY_ID


def test_suppressed_accessible_with_good_key(env):
    # Stash the token, and wipe it out, so the API
    # calls will fail.
    f = cons(env, "api_v2_0_0")
    failed_count = 0
    for thunk in [
        lambda: f(
            "suppressed_notes_to_sefa", ["report_id", "content", "is_minimis_rate_used"]
        ),
        lambda: f("suppressed_findings_text", ["report_id", "finding_ref_number"]),
        lambda: f(
            "suppressed_corrective_action_plans",
            ["report_id", "finding_ref_number", "planned_action"],
        ),
    ]:
        try:
            thunk()
        except:
            failed_count += 1
    assert failed_count == 0
