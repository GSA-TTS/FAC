from django.utils import timezone as django_timezone
import json
import logging
import requests
import ssl
from typing import Optional
import urllib3

from django.conf import settings
from jsonschema import validate
from jsonschema.exceptions import ValidationError


from audit.models import UeiValidationWaiver
from config.settings import SAM_API_URL, SAM_API_KEY, GSA_FAC_WAIVER
from audit.models.utils import one_month_from_today
from django.db.models import Q

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
    actives = filter_actives(entries, filter_field)

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


def is_uei_valid(uei):
    try:
        with open(f"{settings.OUTPUT_BASE_DIR}/UeiSchema.json") as schema:
            schema_json = json.load(schema)
            uei_schema = schema_json.get("properties")["uei"]
            validate(instance=uei, schema=uei_schema)
            return True
    except ValidationError:
        return False
    except Exception:
        return False
    return False


def check_is_uei_valid(uei):
    is_valid = is_uei_valid(uei)
    if not is_valid:
        return {
            "valid": False,
            "errors": ["UEI does not match pattern defined by SAM.gov"],
        }
    else:
        return {"valid": True}


# AUTOMATIC WAIVERS
# We decided to implement this in the event that there is no one to update the API
# key for SAM.gov, or significant interruption to SAM services. We handle the following
# 4xx errors by automatically granting a waiver to the UEI.
automatic_waiver_4xx_codes = [401, 403, 404, 405, 406, 410, 418, 429, 451]


def create_waiver_if_not_exists(uei, resp):
    # If a validation waiver exists for this UEI, and
    # it is currently active---meaning that the waiver expiration date
    # is sometime in the future---log and return
    if UeiValidationWaiver.objects.filter(
        Q(uei=uei) & Q(expiration__gt=django_timezone.now())
    ):
        logger.info(f"WAIVER: Active waiver exists UEI[{uei}]")
        return
    else:
        # If there is no active waiver for this UEI, grant one now.
        # Granting a 30 day waiver; they need to complete the first three steps
        # in that time, which should be easily achieved.
        waiver = UeiValidationWaiver()
        waiver.uei = uei
        waiver.expiration = one_month_from_today()
        waiver.approver_email = "fac_automatic_approver@fac.gsa.gov"
        waiver.approver_name = "Federal Audit Clearinghouse System"
        waiver.requester_email = "fac_automatic_requester@fac.gsa.gov"
        waiver.requester_name = f"SAM.gov {resp.status_code}"
        waiver.justification = json.dumps(
            {
                "status_code": resp.status_code,
                "reason": resp.reason,
                "justification": "This is an automatically issued waiver in the event of a SAM.gov error response.",
                "uei": uei,
            }
        )
        waiver.save()
        logger.info(f"WAIVER: Waiver granted UEI[{uei}]")


def get_uei_info_step_1(uei, api_params, api_headers):
    resp, error = call_sam_api(SAM_API_URL, api_params, api_headers)

    if resp is None:
        return {"valid": False, "errors": [error]}
    if resp.status_code in automatic_waiver_4xx_codes:
        # We need to handle the case where no one is able to update the API key.
        # See ADR https://github.com/GSA-TTS/FAC/issues/4861
        create_waiver_if_not_exists(uei, resp)
        return get_placeholder_sam403(uei)
    if resp.status_code != 200:
        error = f"SAM.gov API response status code invalid: {resp.status_code}"
        return {"valid": False, "errors": [error]}
    results = parse_sam_uei_json(resp.json(), "registrationStatus")
    if results["valid"] and (not results.get("errors")):
        return results


def get_uei_info_step_2(api_params, api_headers):
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
    return resp


def get_uei_info_step_3(uei, resp):
    waiver = UeiValidationWaiver.objects.filter(
        uei=uei, expiration__gte=django_timezone.now()
    ).first()
    if not waiver:
        return {"valid": False, "errors": ["UEI was not found in SAM.gov"]}

    logger.info(f"ueiValidationWaiver applied for {waiver}")

    # 3a. Take the first samRegistered "No" from step 2, regardless of ueiStatus.
    results = parse_sam_uei_json(resp.json(), "_")
    if results["valid"] and (not results.get("errors")):
        return results

    # 3b. Worst case. Let it through with a placeholder name and no other data.
    return get_placeholder_sam(uei)


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

    # First, decide if this is a well-shaped UEI.
    # Because we now handle 4xx errors differently, we should move
    # a well-shaped test here, otherwise poorly-shaped UEIs could make it
    # through and be validated as OK. Let's enforce our schema pattern.
    uei_check = check_is_uei_valid(uei)
    if not uei_check["valid"]:
        return uei_check

    # SAM API Params
    api_params = {
        "ueiSAM": uei,
        "samRegistered": "Yes",
        "includeSections": "entityRegistration,coreData",
    }

    # SAM API headers
    api_headers = {"X-Api-Key": SAM_API_KEY}

    # 1. Best case. samRegistered "Yes"
    step_1_result = get_uei_info_step_1(uei, api_params, api_headers)
    if step_1_result:
        return step_1_result

    # 2. Check samRegistered "No"
    step_2_result = get_uei_info_step_2(api_params, api_headers)
    # We will either get a dictionary or a response object here.
    # A dictionary goes back to the frontent.
    # A response object is needed in step three.
    if isinstance(step_2_result, dict):
        return step_2_result

    # 3. Check for a waiver.
    return get_uei_info_step_3(uei, step_2_result)


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


def get_placeholder_sam403(uei: str) -> dict:
    """
    Return a dictionary with placeholder data as though it were parsed from SAM.gov.
    Only provides placeholders for required fields, to unblock UEIs with waivers.
    This variation is for when we're automating a waiver due to a 403 response.
    """
    placeholder_entry = {
        "coreData": {},
        "entityRegistration": {
            "legalBusinessName": "to be entered",
            "ueiSAM": uei,
        },
    }

    return {"valid": True, "response": placeholder_entry}


def filter_actives(entries, filter_field):
    """
    Filter function. Given a list of entries and a filter field, returns a list of
    entries that are "Active" on that field.

    An entry is kept if the value on the filter field is non-case sensitive "ACTIVE".
    An entry is not kept otherwise, or if the shape of the entry is wrong.
    """

    def is_active(entry):
        if isinstance(entry, dict):
            return entry["entityRegistration"].get(filter_field, "").upper() == "ACTIVE"
        else:
            return False

    return list(filter(is_active, entries))
