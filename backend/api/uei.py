import requests

from config.settings import SAM_API_URL, SAM_API_KEY


def call_sam_api(params: dict) -> tuple[requests.Response, str]:
    """
    Call the SAM.gov API and return the response and/or error string
    """
    try:
        return requests.get(SAM_API_URL, params=params, verify=False), None

    except requests.exceptions.Timeout:
        error = "SAM.gov API timeout"
    except requests.exceptions.TooManyRedirects:
        error = "SAM.gov API error - too many redirects"
    except requests.exceptions.RequestException as e:
        error = f"Unable to make SAM.gov API request, error: {str(e)}"
    except Exception as e:
        error = f"Uncaught SAM.gov API request exception: {str(e)}"
    return None, error


def get_uei_info_from_sam_gov(uei):
    """
    This utility function will query sam.gov to determine the status and
    return information about a provided UEI (or throws an Exception)
    """

    # SAM API Params
    api_params = {
        "api_key": SAM_API_KEY,
        "ueiSAM": uei,
        "samRegistered": "Yes",
        "includeSections": "entityRegistration",
    }

    # Call the SAM API
    r, error = call_sam_api(api_params)
    if not r:
        return {"valid": False, "errors": [error]}

    # Get the status code
    if r.status_code == 200:
        # Load the response json data
        response = r.json()

        # Ensure the UEI exists in SAM.gov
        if response.get("totalRecords") != 1:
            return {"valid": False, "errors": ["UEI was not found in SAM.gov"]}

        entries = response.get("entityData", [])
        if len(entries) != 1:
            return {
                "valid": False,
                "errors": ["SAM.gov invalid number of entries"],
            }
        entry = entries[0]
        try:
            status = (
                entry.get("entityRegistration", {})
                .get("ueiStatus", "")
                .upper()
            )
        except AttributeError:
            return {
                "valid": False,
                "errors": ["SAM.gov unexpected JSON shape"],
            }

        if status != "ACTIVE":
            return {
                "valid": False,
                "errors": [
                    "UEI is not listed as active from SAM.gov response data"
                ],
            }

        return {"valid": True, "response": response["entityData"][0]}

    return {
        "valid": False,
        "errors": [
            f"SAM.gov API response status code invalid, status code: {r.status_code}"
        ],
    }
