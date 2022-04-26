import json
import os
import requests


SAM_API_URL = "https://api.sam.gov/entity-information/v3/entities"
SAM_API_KEY = os.environ.get('SAM_API_KEY')


def get_uei_info_from_sam_gov(uei):
    """
    This utility function will query sam.gov to determine the status and 
    return information about a provided UEI (or throws an Exception)
    """
    response = {}
    errors = []

    # Call the SAM API
    r = requests.get(SAM_API_URL, params={"api_key": SAM_API_KEY, "ueiSAM": uei, "includeSections": "entityRegistration"})

    # Get the status code
    if r.status_code is 200:
        # Load the response json data
        response = json.loads(r.json)

        # Validate there's only one record (totalRecords is 1)
        if response['totalRecords'] is not 1:
            errors.append("Invalid number of records returned")
        # UEI from Sam matches what we searched for
        if response['entityData'][0]['entityRegistration']['ueiSAM'].upper() != uei.upper():
            errors.append("Invalid result returned for search")
        # That it's registered
        if response['entityData'][0]['entityRegistration']['samRegistered'].upper() != "YES":
            errors.append("UEI is listed as not registered")
        # UEI status is active
        if response['entityData'][0]['entityRegistration']['ueiStatus'].upper() != "ACTIVE":
            errors.append("UEI is listed as not active")

    else:
        # API call error
        errors.append("API call did not return correctly")

    # Verify error length < 1
    if len(errors) > 0:
        raise Exception(errors)

    # Return the entity data
    return response['entityData'][0]
