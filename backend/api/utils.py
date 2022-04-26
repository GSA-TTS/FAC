import json
import requests

fake_uei_results = {
    status_code: 200,
    json: {
        "totalRecords": 1,
        "entityData": [
            {
                "entityRegistration": {
                    "samRegistered": "Yes",
                    "ueiSAM": "ZQGGHJH74DW7",
                    "entityEFTIndicator": null,
                    "cageCode": "855J5",
                    "dodaac": null,
                    "legalBusinessName": "INTERNATIONAL BUSINESS MACHINES CORPORATION",
                    "dbaName": null,
                    "purposeOfRegistrationCode": "Z2",
                    "purposeOfRegistrationDesc": "All Awards",
                    "registrationStatus": "Inactive",
                    "evsSource": "D&B",
                    "registrationDate": "2018-07-24",
                    "lastUpdateDate": "2022-03-29",
                    "registrationExpirationDate": "2022-02-06",
                    "activationDate": "2020-08-13",
                    "ueiStatus": "Active",
                    "ueiExpirationDate": null,
                    "ueiCreationDate": "2020-05-01",
                    "publicDisplayFlag": "Y",
                    "exclusionStatusFlag": "N",
                    "exclusionURL": null,
                    "dnbOpenData": null
                }
            }
        ],
        "links": {
            "selfLink": "https://api.sam.gov/entity-information/v3/entities?api_key=REPLACE_WITH_API_KEY&ueiSAM=ZQGGHJH74DW7&includeSections=entityRegistration&page=0&size=10"
        }
    }
}

def get_uei_info_from_samgov(self, uei):
    """
    This utility function will query sam.gov to determine the status and 
    information about a provided UEI
    """

    # Validate the UEI using the SAM.gov API
    samAPIURL = "https://api.sam.gov/entity-information/v3/entities?api_key=<APIKey>&ueiSAM=ZQGGHJH74DW7&includeSections=entityRegistration"

    # response = {}
    errors = []
    #r = requests.get(samAPIURL)
    r = fake_uei_results

    if r.status_code is 200:
        # Validate there's only one record (totalRecords is 1)
            if r.json.total_records is not 1:
                errors.append("Invalid number of records returned")
        # UEI from Sam matches what we searched for
            if r.json.entityData.entityRegistration.ueiSAM.upper() != uei.upper():
                errors.append("Invalid result returned for search")
        # That it's registered
            if r.json.entityData.entityRegistration.samRegistered.upper() != "YES":
                errors.append("UEI is listed as not registered")
        # UEI status is active
            if r.json.entityData.entityRegistration.ueiStatus.upper() != "ACTIVE":
                errors.append("UEI is listed as not active")      
        # Should be valid!

    else:
        # API call error
        errors.append("API call did not return correctly")
    
    if errors.length > 0:
        raise Exception(errors)
    
    return r.json.entityData
