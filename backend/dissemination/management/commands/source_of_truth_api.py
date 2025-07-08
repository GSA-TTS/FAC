from django.core.management.base import BaseCommand
from django.conf import settings

import logging
import requests
import sys

logger = logging.getLogger(__name__)

API_GOV_USER_ID = "a1f6d8fd-c39a-49fe-ab0a-82e8a8fa6d5b"
# API_GOV_USER_ID = os.environ.get("API_GOV_USER_ID")
API_GOV_JWT = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoiYXBpX2ZhY19nb3YiLCJjcmVhdGVkIjoiMjAyMy0wOS0xOVQxMDowMToxMi4zNTkzNTEifQ.uHOTzHp7sN_8tLftFYcva-5m6CQMrauY0DyIPAIZXpw"
# API_GOV_JWT = os.environ.get("API_GOV_JWT")
API_GOV_KEY = "R7SYmSzraSfsF9OvgwxadjjmfSUg3TgdKZP7KbuI"
# API_GOV_KEY = os.environ.get("API_GOV_KEY")
API_GOV_URL = "localhost:3000"

SAC_API = "api_v1_1_0"
SOT_API = "api_v1_1_0"  # TODO: Update this once the SOT api is ready

endpoints = [
    # /general is a special case, as it's used to find the report_ids that will
    # be used to query the endpoints below
    "federal_awards",
    "notes_to_sefa",
    "findings",
    "findings_text",
    "corrective_action_plans",
    "passthrough",
    "secondary_auditors",
    "additional_ueis",
    "additional_eins",
]


class Command(BaseCommand):
    help = """
        For the given fac_accepted_date range, validate that submission data
        matches for both the SOT and SAC APIs.
        Usage:
        manage.py source_of_truth_api
            --start <YYYYMMDD start fac_accepted_date>
            --end <YYYYMMDD end fac_accepted_date>

        Alternatively, it can also test on a single report_id:
        manage.py source_of_truth_api
            --report_id 2023-12-GSAFAC-0000000001
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--start", type=str, required=False, help="YYYYMMDD start fac_accepted_date"
        )
        parser.add_argument(
            "--end", type=str, required=False, help="YYYYMMDD end fac_accepted_date"
        )
        parser.add_argument("--report_id", type=str, required=False, help="A report_id")
        parser.add_argument(
            "--verbose", action="store_true", help="Enable verbose output"
        )

    def handle(self, *args, **kwargs):
        self.start = kwargs.get(kwargs["start"], None)
        self.end = kwargs.get(kwargs["end"], None)
        self.report_id = kwargs.get("report_id", None)
        self.verbose = kwargs.get("verbose", None)

        if not (self.start and self.end) and not self.report_id:
            logger.error(
                "Either --start and --end must be supplied, or --report_id. Exiting."
            )
            sys.exit(1)

        sac_response_json = self._fetch_general_for_api(SAC_API)
        sac_sorted_report_ids = self._get_sorted_report_ids(sac_response_json)
        logger.info(f"{len(sac_sorted_report_ids)} SAC audits found")

        sot_response_json = self._fetch_general_for_api(SOT_API)
        sot_sorted_report_ids = self._get_sorted_report_ids(sot_response_json)
        logger.info(f"{len(sot_sorted_report_ids)} SOT audits found")

        self._validate_sac_sot_report_ids(sac_sorted_report_ids, sot_sorted_report_ids)

        # Both report_id lists are the same and sorted doesn't matter anymore
        report_ids = sac_sorted_report_ids

        sac_audits_by_report_id = self._get_data_by_report_id(sac_response_json)
        sot_audits_by_report_id = self._get_data_by_report_id(sot_response_json)
        differences_by_endpoint = {}
        differences = self._get_endpoint_differences(
            report_ids,
            sac_audits_by_report_id,
            sot_audits_by_report_id,
            is_general=True,
        )

        if differences:
            differences_by_endpoint["general"] = differences

        for endpoint in endpoints:
            sac_response_json = self._fetch_endpoint_data_for_report_ids(
                endpoint, report_ids, SAC_API
            )
            sac_data_by_report_id = self._get_data_by_report_id(sac_response_json)
            sot_response_json = self._fetch_endpoint_data_for_report_ids(
                endpoint, report_ids, SOT_API
            )
            sot_data_by_report_id = self._get_data_by_report_id(sot_response_json)

            differences = self._get_endpoint_differences(
                report_ids, sac_data_by_report_id, sot_data_by_report_id
            )
            if differences:
                differences_by_endpoint[endpoint] = differences

        if differences_by_endpoint:
            logger.error("Differences found:")
            logger.error(differences_by_endpoint)
            sys.exit(1)
        else:
            logger.info("No differences found")

    def _validate_sac_sot_report_ids(
        self, sac_sorted_report_ids, sot_sorted_report_ids
    ):
        """
        If the given list of sorted report_ids aren't equal, it logs the
        differences and exits
        """
        if sac_sorted_report_ids != sot_sorted_report_ids:
            sot_not_sac = [
                x for x in sot_sorted_report_ids if x not in sac_sorted_report_ids
            ]
            logger.error(f"report_ids found in SOT but not SAC: {sot_not_sac}")
            sac_not_sot = [
                x for x in sac_sorted_report_ids if x not in sot_sorted_report_ids
            ]
            logger.error(f"report_ids found in SAC but not SOT: {sac_not_sot}")
            logger.error("Exiting.")
            sys.exit(1)
        else:
            logger.info("SOT and SAC report_ids match; continuing")

    def _get_endpoint_differences(
        self, report_ids, sac_data_by_report_id, sot_data_by_report_id, is_general=False
    ):
        """
        Returns the differences for the given SAC and SOT endpoint dicts,
        keyed by report_id
        """
        differences = {}

        for report_id in report_ids:
            sac_entries_for_report_id = sac_data_by_report_id.get(report_id, [])
            sot_entries_for_report_id = sot_data_by_report_id.get(report_id, [])

            # The results from /general are a single entry per report_id, so we can directly compare them
            if (
                is_general
                and len(sac_entries_for_report_id) == 1
                and len(sac_entries_for_report_id) == 1
            ):
                sac_entry = sac_entries_for_report_id[0]
                sot_entry = sot_entries_for_report_id[0]

                if sac_entry != sot_entry:
                    if self.verbose:
                        differences[report_id] = {}

                        for field in sac_entry:
                            sac_value = sac_entry[field]
                            sot_value = sac_entry[field]

                            if sac_value != sot_value:
                                differences[report_id] = {
                                    "field": field,
                                    "sac_value": sac_value,
                                    "sot_value": sot_value,
                                }
                    else:
                        differences[report_id] = "Data does not match"
            else:
                # Entries found in SAC but not SOT
                self._get_differences_for_entries(
                    sac_entries_for_report_id,
                    sot_entries_for_report_id,
                    report_id,
                    "sac_not_sot",
                    differences,
                )
                # Entries found in SOT but not SAC
                self._get_differences_for_entries(
                    sot_entries_for_report_id,
                    sac_entries_for_report_id,
                    report_id,
                    "sot_not_sac",
                    differences,
                )

                # for entry in sac_entries_for_report_id:
                #     if not self._entry_found_in_list(entry, sot_entries_for_report_id):
                #         if not differences.get(report_id):
                #             differences[report_id] = {}
                #         if not differences.get(report_id).get("sac_not_sot"):
                #             differences[report_id] = { "sac_not_sot": [] }
                #         differences[report_id]["sac_not_sot"].append(entry)

                # for entry in sot_entries_for_report_id:
                #     if not self._entry_found_in_list(entry, sot_entries_for_report_id):
                #         if not differences.get(report_id):
                #             differences[report_id] = {}
                #         if not differences.get(report_id).get("sot_not_sac"):
                #             differences[report_id] = { "sot_not_sac": [] }
                #         differences[report_id]["sot_not_sac"].append(entry)

        return differences

    def _get_differences_for_entries(
        self, entries_1, entries_2, report_id, diff_key, differences
    ):
        """
        Adds to differences all entries from entries_1 that are not found
        within entries_2
        """
        for entry in entries_1:
            if not self._entry_found_in_list(entry, entries_2):
                if not differences.get(report_id):
                    differences[report_id] = {}
                if not differences.get(report_id).get(diff_key):
                    differences[report_id] = {[diff_key]: []}
                differences[report_id][diff_key].append(entry)

    def _entry_found_in_list(self, dict_to_find, dict_list):
        """
        Returns True if the given dict is found within the given list of dicts,
        and False otherwise
        """
        for cur_dict in dict_list:
            if cur_dict == dict_to_find:
                return True

        return False

    def _fetch_endpoint_data_for_report_ids(self, endpoint, report_ids, api):
        """
        Perform a FAC GET request for the given endpoint, report_ids, and API
        """
        params = {
            "report_id": f"in.({','.join(report_ids)})",
        }
        return self._fetch(endpoint, params, api)

    def _fetch_general_for_api(self, api):
        """Perform a FAC GET request for /general for the given API"""
        if self.report_id:
            logger.info(f"Searching on report_id {self.report_id}")
            params = {
                "report_id": f"eq.{self.report_id}",
            }
        else:
            logger.info(f"Searching on {self.start}-{self.end}")
            params = {
                "and": f"(fac_accepted_date.gte.{self.start},fac_accepted_date.lte.{self.end})",
            }

        return self._fetch("general", params, api)

    def _fetch(self, endpoint, params, api):
        """Perform a FAC GET request for the given endpoint, params, and API"""
        query_url = f"{settings.POSTGREST.get('URL')}/{endpoint}"
        response = requests.get(
            query_url,
            params,
            headers={
                "Authorization": f"Bearer {API_GOV_JWT}",
                "X-Api-Key": API_GOV_KEY,
                "Accept-Profile": api,
                "X-Api-User-Id": API_GOV_USER_ID,
            },
        )

        return response.json()

    def _get_sorted_report_ids(self, response_json):
        """
        Return a sorted list of the report_ids found in the given JSON response
        """
        report_ids = []
        for audit in response_json:
            report_ids.append(audit["report_id"])

        report_ids.sort()

        return report_ids

    def _get_data_by_report_id(self, json_response):
        """
        Returns a dict that maps report_ids to their entry in the given JSON
        response
        """
        result = {}

        for data in json_response:
            report_id = data["report_id"]
            if not result.get(report_id):
                result[report_id] = []

            result[report_id].append(data)

        return result
