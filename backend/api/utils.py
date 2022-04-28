import requests

from config.settings import SAM_API_URL, SAM_API_KEY


def get_uei_info_from_sam_gov(uei):
    """
    This utility function will query sam.gov to determine the status and 
    return information about a provided UEI (or throws an Exception)
    """
    export = {
        "valid": False
    }
    errors = []

    # SAM API Params
    api_params = {
        "api_key": SAM_API_KEY,
        "ueiSAM": uei,
        "samRegistered": "Yes",
        "includeSections": "entityRegistration"
    }

    # Call the SAM API
    try:
        r = requests.get(SAM_API_URL, params=api_params, verify=False)

        # Get the status code
        if r.status_code == 200:
            # Load the response json data
            response = r.json()

            # Ensure the UEI exists in SAM.gov
            if response.get('totalRecords') != 1:
                errors.append("UEI was not found in SAM.gov")

            # UEI status is active
            if response.get('entityData') and response.get('entityData')[0].get('entityRegistration').get('ueiStatus').upper() != "ACTIVE":
                errors.append("UEI is not listed as active from SAM.gov response data")

        else:
            # API call error
            errors.append("SAM.gov API response status code invalid, status code: " + str(r.status_code))

    except requests.exceptions.Timeout:
        # Timeout error
        errors.append("SAM.gov API timeout")
    except requests.exceptions.TooManyRedirects:
        # Too many redirects
        errors.append("SAM.gov API error - too many redirects")
    except requests.exceptions.RequestException as e:
        # Catastrophic error
        errors.append("Unable to make SAM.gov API request, error: " + str(e))
    except KeyError:
        errors.append("SAM.gov response key error, unable to validate entityData")
    except Exception as e:
        errors.append("Uncaught SAM.gov API request exception: " + str(e))

    # Verify error length < 1
    if errors:
        export["errors"] = errors
        return export

    # Valid UEI and API response
    export["valid"] = True
    export["response"] = response['entityData'][0]

    # Return the entity data
    return export
