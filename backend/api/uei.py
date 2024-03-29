from typing import Optional
import ssl
import urllib3
import requests

from config.settings import SAM_API_URL, SAM_API_KEY


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


def parse_sam_uei_json(response: dict) -> dict:
    """
    Parse the SAM.gov response dictionary, which requires some vetting to get
    at the nested values we want to check.

    Primarily we want to know that the totalRecords value is one, that there's
    only one item in entityData, that item is a dictionary which can be
    queried for an item["entityRegistration"]["ueiStatus"] value
    case-insensitively equal to "active", and that entityData can be queried
    for an item["coreData"]["entityInformation"]["fiscalYearEndCloseDate"] value.
    """
    # Ensure the UEI exists in SAM.gov
    if response.get("totalRecords", 0) < 1:
        return {"valid": False, "errors": ["UEI was not found in SAM.gov"]}

    # Ensure there's only one entry:
    # Nope! 2023-10-05: turns out you can get multiple valid entries.
    entries = response.get("entityData", [])
    if len(entries) > 1:

        def is_active(entry):
            return entry["entityRegistration"]["registrationStatus"] == "Active"

        actives = list(filter(is_active, entries))
        if actives:
            entry = actives[0]
        else:
            entry = entries[0]
    elif len(entries) == 1:
        entry = entries[0]
    else:
        return {"valid": False, "errors": ["UEI was not found in SAM.gov"]}

    # Get the ueiStatus and catch errors if the JSON shape is unexpected:
    try:
        _ = entry.get("entityRegistration", {}).get("ueiStatus", "").upper()
    except AttributeError:
        return {
            "valid": False,
            "errors": ["SAM.gov unexpected JSON shape"],
        }

    # 2023-10-05 comment out the following, as checking for this creates more
    # problems for our users than it's worth.
    # Ensure the status is active:
    # if status != "ACTIVE":
    #     return {
    #         "valid": False,
    #         "errors": ["UEI is not listed as active from SAM.gov response data"],
    #     }

    # Get the fiscalYearEndCloseDate and catch errors if the JSON shape is unexpected:
    try:
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
    return information about a provided UEI (or throws an Exception)
    """

    # SAM API Params
    api_params = {
        "ueiSAM": uei,
        "samRegistered": "Yes",
        "includeSections": "entityRegistration,coreData",
    }

    # SAM API headers
    api_headers = {"X-Api-Key": SAM_API_KEY}

    # Call the SAM API
    resp, error = call_sam_api(SAM_API_URL, api_params, api_headers)
    if resp is None:
        return {"valid": False, "errors": [error]}

    # Get the response status code
    if resp.status_code != 200:
        error = f"SAM.gov API response status code invalid: {resp.status_code}"
        return {"valid": False, "errors": [error]}

    results = parse_sam_uei_json(resp.json())
    if results["valid"] and (not results.get("errors")):
        return results

    # Try again with samRegistered set to No:
    api_params = api_params | {"samRegistered": "No"}
    # Call the SAM API
    resp, error = call_sam_api(SAM_API_URL, api_params, api_headers)
    if resp is None:
        return {"valid": False, "errors": [error]}

    # Get the response status code
    if resp.status_code != 200:
        error = f"SAM.gov API response status code invalid: {resp.status_code}"
        return {"valid": False, "errors": [error]}

    return parse_sam_uei_json(resp.json())
