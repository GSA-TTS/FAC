import logging
import requests
import ssl
from typing import Optional
import urllib3

from audit.models import UeiValidationWaiver
from config.settings import SAM_API_URL, SAM_API_KEY, GSA_FAC_WAIVER

logger = logging.getLogger(__name__)


class CustomHttpAdapter(requests.adapters.HTTPAdapter):
    """Transport adapter that allows us to use custom ssl_context."""

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def proxy_manager_for(self, *args, **kwargs):  # pragma: no cover
        kwargs["ssl_context"] = self.ssl_context
        return super().proxy_manager_for(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, *_args, block=False, **_kwds):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=self.ssl_context,
        )


_ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
_ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
SESSION = requests.session()
SESSION.mount("https://", CustomHttpAdapter(_ctx))


def call_sam_api(
    sam_api_url: str, params: dict, headers: dict
) -> tuple[Optional[requests.Response], Optional[str]]:
    """
    Call the SAM.gov API and return the response and/or error string

    SAM.gov uses a legacy version of SSL that OpenSSL 3 rejects. We specify
    just in this one spot the magic flag 0x04 corresponding to
    ssl.OP_LEGACY_SERVER_CONNECT for the SSL context.
    """
    try:
        return (
            SESSION.get(sam_api_url, params=params, headers=headers, timeout=15),
            None,
        )

    except requests.exceptions.Timeout:
        error = "SAM.gov API timeout"
    except requests.exceptions.TooManyRedirects:
        error = "SAM.gov API error - too many redirects"
    except requests.exceptions.RequestException as err:
        error = f"Unable to make SAM.gov API request, error: {str(err)}"
    return None, error


def parse_sam_uei_json(response: dict, filter_field: str) -> dict:
    """
    Parse the SAM.gov response dictionary, which requires some vetting to get
    at the nested values we want to check.

    Primarily we want to know that at least one record is found, and that it matches
    our desired filters. A valid record is a dictionary which can be queried for an
    item["entityRegistration"]["ueiStatus"] value case-insensitively equal to "active",
    and that entityData can be queried for an
    item["coreData"]["entityInformation"]["fiscalYearEndCloseDate"] value.
    """
    # Ensure at least one record was found
    if response.get("totalRecords", 0) < 1:
        return {"valid": False, "errors": ["UEI was not found in SAM.gov"]}

    entries = response.get("entityData", [])
    if len(entries) == 0:
        return {"valid": False, "errors": ["UEI was not found in SAM.gov"]}

    # Separate out the entries that are "active" on the filter_field
    def is_active(entry):
        return entry["entityRegistration"][filter_field].upper() == "ACTIVE"

    actives = list(filter(is_active, entries))

    # If there are one or more "active" entries on the filter_field, take the first.
    # Otherwise, take or reject the first non-active depending on the field.
    if actives:
        entry = actives[0]
    elif filter_field == "registrationStatus":
        entry = entries[0]
    elif filter_field == "ueiStatus":
        return {"valid": False, "errors": ["UEI was not found in SAM.gov"]}
    elif filter_field == "_":
        entry = entries[0]

    # Make sure the ueiStatus and fiscalYearEndCloseDate exist and catch errors if the JSON shape is unexpected:
    try:
        _ = entry.get("entityRegistration", {}).get("ueiStatus", "").upper()
        _ = (
            entry.get("coreData", {})
            .get("entityInformation", {})
            .get("fiscalYearEndCloseDate", "")
        )
    except AttributeError:
        return {
            "valid": False,
            "errors": ["SAM.gov unexpected JSON shape"],
        }

    # Return valid response
    return {"valid": True, "response": entry}


def get_uei_info_from_sam_gov(uei: str) -> dict:
    """
    This utility function will query sam.gov to determine the status and
    return information about a provided UEI (or throws an Exception).

    In the case of a UEI validation waiver, either takes the exisiting inactive
    UEI or provides placeholder data.

    UEI checks in order:
    1. Best case. Check for samRegistered "Yes". If one exists, take it.
    If there are several, use the first with registrationStatus "Active".
    2. Check for samRegistered "No". Take it as long as the ueiStatus is "Active".
    3. Check for a waiver:
          a. Check for that possibly non-registered, inactive UEI.
          b. Worst case: Let it through with a placeholder name.
    """
    # SAM API Params
    api_params = {
        "ueiSAM": uei,
        "samRegistered": "Yes",
        "includeSections": "entityRegistration,coreData",
    }

    # SAM API headers
    api_headers = {"X-Api-Key": SAM_API_KEY}

    # 1. Best case. samRegistered "Yes"
    resp, error = call_sam_api(SAM_API_URL, api_params, api_headers)
    if resp is None:
        return {"valid": False, "errors": [error]}
    if resp.status_code != 200:
        error = f"SAM.gov API response status code invalid: {resp.status_code}"
        return {"valid": False, "errors": [error]}
    results = parse_sam_uei_json(resp.json(), "registrationStatus")
    if results["valid"] and (not results.get("errors")):
        return results

    # 2. Check samRegistered "No"
    api_params = api_params | {"samRegistered": "No"}
    resp, error = call_sam_api(SAM_API_URL, api_params, api_headers)
    if resp is None:
        return {"valid": False, "errors": [error]}
    if resp.status_code != 200:
        error = f"SAM.gov API response status code invalid: {resp.status_code}"
        return {"valid": False, "errors": [error]}
    results = parse_sam_uei_json(resp.json(), "ueiStatus")
    if results["valid"] and (not results.get("errors")):
        return results

    # 3. Check for a waiver.
    waiver = UeiValidationWaiver.objects.filter(uei=uei).first()
    if not waiver:
        return {"valid": False, "errors": ["UEI was not found in SAM.gov"]}

    logger.info(f"ueiValidationWaiver applied for {waiver}")

    # 3a. Take the first samRegistered "No" from step 2, regardless of ueiStatus.
    results = parse_sam_uei_json(resp.json(), "_")
    if results["valid"] and (not results.get("errors")):
        return results

    # 3b. Worst case. Let it through with a placeholder name and no other data.
    return get_placeholder_sam(uei)


def get_placeholder_sam(uei: str) -> dict:
    """
    Return a dictionary with placeholder data as though it were parsed from SAM.gov.
    Only provides placeholders for required fields, to unblock UEIs with waivers.
    """
    placeholder_entry = {
        "coreData": {},
        "entityRegistration": {
            "legalBusinessName": GSA_FAC_WAIVER,
            "ueiSAM": uei,
        },
    }

    return {"valid": True, "response": placeholder_entry}
