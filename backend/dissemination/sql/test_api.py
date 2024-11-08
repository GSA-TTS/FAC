from django.test import TestCase
import os
import requests
import sys
import uuid


class EnvVars:
    FAC_API_KEY = os.getenv("FAC_API_KEY")
    FAC_API_KEY_ID = os.getenv("CYPRESS_API_GOV_USER_ID")
    FAC_AUTH_BEARER = os.getenv("CYPRESS_API_GOV_JWT")
    RECORDS_REQUESTED = 5
    CAN_READ_SUPPRESSED = (
        str(os.getenv("CAN_READ_SUPPRESSED"))
        if os.getenv("CAN_READ_SUPPRESSED") is not None
        else "0"
    )


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
        if EnvVars.FAC_AUTH_BEARER is None:
            print("FAC_AUTH_BEARER not set.")
            sys.exit()
        if EnvVars.FAC_API_KEY_ID is None:
            print("FAC_API_KEY_ID not set.")
            sys.exit()
        return {
            "authorization": f"bearer {EnvVars.FAC_AUTH_BEARER}",
            "x-api-user-id": EnvVars.FAC_API_KEY_ID,
        }
    elif env in ["preview", "dev", "staging", "production"]:
        if EnvVars.FAC_API_KEY is None:
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


class ApiTests(TestCase):

    ENV = "local"

    def good_resp(self, objs, keys):
        """
        Asserts that an API response is:
        * A list
        * A list composed of objects that all contain the required keys
        """
        self.assertIsInstance(objs, list)
        self.assertEqual(len(objs), EnvVars.RECORDS_REQUESTED)
        for k in keys:
            for o in objs:
                self.assertIn(k, o)
        return True

    def cons(self, env, api_version):
        """Constructs the base URL for making multiple API calls off of."""

        # FIXME: currently, both tests that use this method fail over a "ConnectionRefusedError".
        def _helper(endpoint, keys):
            base = url(env)
            h = (
                headers(env)
                | limit(0, EnvVars.RECORDS_REQUESTED - 1)
                | api(api_version)
            )
            r = requests.get(base + f"/{endpoint}", headers=h)
            self.good_resp(r.json(), keys)

        return _helper

    def common_tables(self, f):
        """These tables are common to both the old API and the new public data API."""

        f("general", ["report_id", "audit_year", "auditee_name"])
        f(
            "federal_awards",
            ["report_id", "amount_expended", "audit_report_type"],
        )
        f("corrective_action_plans", ["report_id", "finding_ref_number", "auditee_uei"])

    def test_api_v1_0_3_not_exist(self):
        f = self.cons(self.ENV, "api_v1_0_3")
        try:
            self.common_tables(f)
            print("This schema/API should not exist.")
            self.assertTrue(False)
        except Exception:
            pass

    def test_api_v1_1_0(self):
        f = self.cons(self.ENV, "api_v1_1_0")
        self.common_tables(f)

    def test_api_v2_0_0(self):
        f = self.cons(self.ENV, "api_v2_0_0")
        self.common_tables(f)

    def test_suppressed_not_accessible_with_bad_key(self):
        # Stash the token, and wipe it out, so the API
        # calls will fail.
        TEMP_FAC_API_KEY_ID = EnvVars.FAC_API_KEY_ID
        EnvVars.FAC_API_KEY_ID = str(uuid.uuid4())
        f = self.cons(self.ENV, "api_v2_0_0")
        failed_count = 0
        for thunk in [
            lambda: f(
                "suppressed_notes_to_sefa",
                ["report_id", "content", "is_minimis_rate_used"],
            ),
            lambda: f("suppressed_findings_text", ["report_id", "finding_ref_number"]),
            lambda: f(
                "suppressed_corrective_action_plans",
                ["report_id", "finding_ref_number", "planned_action"],
            ),
        ]:
            try:
                thunk()
            except Exception:
                if EnvVars.CAN_READ_SUPPRESSED == "0":
                    failed_count += 1
        self.assertEqual(failed_count, 3)
        # Restore it in case we need it in later tests.
        EnvVars.FAC_API_KEY_ID = TEMP_FAC_API_KEY_ID

    def test_suppressed_accessible_with_good_key(self):
        # Stash the token, and wipe it out, so the API
        # calls will fail.
        f = self.cons(self.ENV, "api_v2_0_0")
        failed_count = 0
        for thunk in [
            lambda: f(
                "suppressed_notes_to_sefa",
                ["report_id", "content", "is_minimis_rate_used"],
            ),
            lambda: f("suppressed_findings_text", ["report_id", "finding_ref_number"]),
            lambda: f(
                "suppressed_corrective_action_plans",
                ["report_id", "finding_ref_number", "planned_action"],
            ),
        ]:
            try:
                thunk()
            except Exception:
                if EnvVars.CAN_READ_SUPPRESSED == "1":
                    failed_count += 1
        self.assertEqual(failed_count, 0)
