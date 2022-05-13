import json

from unittest.mock import patch
from django.test import TestCase
import requests

# from requests.exceptions import Timeout, TooManyRedirects

from api.uei import get_uei_info_from_sam_gov


valid_uei_results_dict = {
    "totalRecords": 1,
    "entityData": [
        {
            "entityRegistration": {
                "samRegistered": "Yes",
                "ueiSAM": "ZQGGHJH74DW7",
                "entityEFTIndicator": None,
                "cageCode": "855J5",
                "dodaac": None,
                "legalBusinessName": "INTERNATIONAL BUSINESS MACHINES CORPORATION",
                "dbaName": None,
                "purposeOfRegistrationCode": "Z2",
                "purposeOfRegistrationDesc": "All Awards",
                "registrationStatus": "Inactive",
                "evsSource": "D&B",
                "registrationDate": "2018-07-24",
                "lastUpdateDate": "2022-03-29",
                "registrationExpirationDate": "2022-02-06",
                "activationDate": "2020-08-13",
                "ueiStatus": "Active",
                "ueiExpirationDate": None,
                "ueiCreationDate": "2020-05-01",
                "publicDisplayFlag": "Y",
                "exclusionStatusFlag": "N",
                "exclusionURL": None,
                "dnbOpenData": None
            },
            "coreData": {
                "entityInformation": {
                    "entityURL": "http://www.ibm.com/us/en",
                    "entityDivisionName": "IBM Global Business Services",
                    "entityDivisionNumber": "16",
                    "entityStartDate": "1911-01-01",
                    "fiscalYearEndCloseDate": "12/31",
                    "submissionDate": "2020-08-10"
                },
                "physicalAddress": {
                    "addressLine1": "306 SENTINEL DR STE 450",
                    "addressLine2": None,
                    "city": "ANNAPOLIS JUNCTION",
                    "stateOrProvinceCode": "MD",
                    "zipCode": "20701",
                    "zipCodePlus4": "1007",
                    "countryCode": "USA"
                },
                "mailingAddress": {
                    "addressLine1": "306 SENTINEL DR STE 450",
                    "addressLine2": None,
                    "city": "ANNAPOLIS JUNCTION",
                    "stateOrProvinceCode": "MD",
                    "zipCode": "20701",
                    "zipCodePlus4": "1007",
                    "countryCode": "USA"
                },
                "congressionalDistrict": "02",
                "generalInformation": {
                    "entityStructureCode": "2L",
                    "entityStructureDesc": "Corporate Entity (Not Tax Exempt)",
                    "entityTypeCode": "F",
                    "entityTypeDesc": "Business or Organization",
                    "profitStructureCode": "2X",
                    "profitStructureDesc": "For Profit Organization",
                    "organizationStructureCode": None,
                    "organizationStructureDesc": None,
                    "stateOfIncorporationCode": "NY",
                    "stateOfIncorporationDesc": "NEW YORK",
                    "countryOfIncorporationCode": "USA",
                    "countryOfIncorporationDesc": "UNITED STATES"
                },
                "businessTypes": {
                    "businessTypeList": [
                        {
                            "businessTypeCode": "2X",
                            "businessTypeDesc": "For Profit Organization"
                        },
                        {
                            "businessTypeCode": "F",
                            "businessTypeDesc": "Business or Organization"
                        }
                    ],
                    "sbaBusinessTypeList": [
                        {
                            "sbaBusinessTypeCode": None,
                            "sbaBusinessTypeDesc": None,
                            "certificationEntryDate": None,
                            "certificationExitDate": None
                        }
                    ]
                },
                "financialInformation": {
                    "creditCardUsage": "N",
                    "debtSubjectToOffset": "N"
                }
            }
        }
    ],
    "links": {
        "selfLink": "".join(
            [
                "https://api.sam.gov/entity-information/v3/entities?",
                "api_key=REPLACE_WITH_API_KEY&",
                "ueiSAM=ZQGGHJH74DW7&",
                "includeSections=entityRegistration%2CcoreData&",
                "page=0&",
                "size=10",
            ]
        )
    },
}
valid_uei_results = json.dumps(valid_uei_results_dict)

invalid_uei_results_dict = {
    "totalRecords": 1,
    "entityData": [
        {
            "entityRegistration": {
                "samRegistered": "Yes",
                "ueiSAM": "ZQGGHJH74DW7",
                "entityEFTIndicator": None,
                "cageCode": "855J5",
                "dodaac": None,
                "legalBusinessName": "INTERNATIONAL BUSINESS MACHINES CORPORATION",
                "dbaName": None,
                "purposeOfRegistrationCode": "Z2",
                "purposeOfRegistrationDesc": "All Awards",
                "registrationStatus": "Inactive",
                "evsSource": "D&B",
                "registrationDate": "2018-07-24",
                "lastUpdateDate": "2022-03-29",
                "registrationExpirationDate": "2022-02-06",
                "activationDate": "2020-08-13",
                "ueiStatus": "Inactive",
                "ueiExpirationDate": None,
                "ueiCreationDate": "2020-05-01",
                "publicDisplayFlag": "Y",
                "exclusionStatusFlag": "N",
                "exclusionURL": None,
                "dnbOpenData": None,
            }
        }
    ],
    "links": {
        "selfLink": "".join(
            [
                "https://api.sam.gov/entity-information/v3/entities?",
                "api_key=REPLACE_WITH_API_KEY&",
                "ueiSAM=ZQGGHJH74DW7&",
                "includeSections=entityRegistration&",
                "page=0&",
                "size=10",
            ]
        )
    },
}
invalid_uei_results = json.dumps(invalid_uei_results_dict)

missing_uei_results = json.dumps({"totalRecords": 0, "entityData": []})
lying_uei_results = json.dumps({"totalRecords": 1, "entityData": []})
misshapen_uei_results = json.dumps({"totalRecords": 1, "entityData": [""]})

inactive_uei_results_dict = {
    "totalRecords": 1,
    "entityData": [
        {
            "entityRegistration": {
                "samRegistered": "Yes",
                "ueiSAM": "ZQGGHJH74DW7",
                "entityEFTIndicator": None,
                "cageCode": "855J5",
                "dodaac": None,
                "legalBusinessName": "INTERNATIONAL BUSINESS MACHINES CORPORATION",
                "dbaName": None,
                "purposeOfRegistrationCode": "Z2",
                "purposeOfRegistrationDesc": "All Awards",
                "registrationStatus": "Inactive",
                "evsSource": "D&B",
                "registrationDate": "2018-07-24",
                "lastUpdateDate": "2022-03-29",
                "registrationExpirationDate": "2022-02-06",
                "activationDate": "2020-08-13",
                "ueiStatus": "Inactive",
                "ueiExpirationDate": None,
                "ueiCreationDate": "2020-05-01",
                "publicDisplayFlag": "Y",
                "exclusionStatusFlag": "N",
                "exclusionURL": None,
                "dnbOpenData": None
            },
            "coreData": {
                "entityInformation": {
                    "entityURL": "http://www.ibm.com/us/en",
                    "entityDivisionName": "IBM Global Business Services",
                    "entityDivisionNumber": "16",
                    "entityStartDate": "1911-01-01",
                    "fiscalYearEndCloseDate": "12/31",
                    "submissionDate": "2020-08-10"
                },
                "physicalAddress": {
                    "addressLine1": "306 SENTINEL DR STE 450",
                    "addressLine2": None,
                    "city": "ANNAPOLIS JUNCTION",
                    "stateOrProvinceCode": "MD",
                    "zipCode": "20701",
                    "zipCodePlus4": "1007",
                    "countryCode": "USA"
                },
                "mailingAddress": {
                    "addressLine1": "306 SENTINEL DR STE 450",
                    "addressLine2": None,
                    "city": "ANNAPOLIS JUNCTION",
                    "stateOrProvinceCode": "MD",
                    "zipCode": "20701",
                    "zipCodePlus4": "1007",
                    "countryCode": "USA"
                },
                "congressionalDistrict": "02",
                "generalInformation": {
                    "entityStructureCode": "2L",
                    "entityStructureDesc": "Corporate Entity (Not Tax Exempt)",
                    "entityTypeCode": "F",
                    "entityTypeDesc": "Business or Organization",
                    "profitStructureCode": "2X",
                    "profitStructureDesc": "For Profit Organization",
                    "organizationStructureCode": None,
                    "organizationStructureDesc": None,
                    "stateOfIncorporationCode": "NY",
                    "stateOfIncorporationDesc": "NEW YORK",
                    "countryOfIncorporationCode": "USA",
                    "countryOfIncorporationDesc": "UNITED STATES"
                },
                "businessTypes": {
                    "businessTypeList": [
                        {
                            "businessTypeCode": "2X",
                            "businessTypeDesc": "For Profit Organization"
                        },
                        {
                            "businessTypeCode": "F",
                            "businessTypeDesc": "Business or Organization"
                        }
                    ],
                    "sbaBusinessTypeList": [
                        {
                            "sbaBusinessTypeCode": None,
                            "sbaBusinessTypeDesc": None,
                            "certificationEntryDate": None,
                            "certificationExitDate": None
                        }
                    ]
                },
                "financialInformation": {
                    "creditCardUsage": "N",
                    "debtSubjectToOffset": "N"
                }
            }
        }
    ],
    "links": {
        "selfLink": "".join(
            [
                "https://api.sam.gov/entity-information/v3/entities?",
                "api_key=REPLACE_WITH_API_KEY&",
                "ueiSAM=ZQGGHJH74DW7&",
                "includeSections=entityRegistration%2CcoreData&",
                "page=0&",
                "size=10",
            ]
        )
    },
}
inactive_uei_results = json.dumps(inactive_uei_results_dict)


class UtilsTesting(TestCase):
    def test_get_uei_info_from_sam_gov(self):
        """
        Tests UEI validation
        """
        test_uei = "ZQGGHJH74DW7"

        # Valid
        with patch("api.uei.requests.get") as mock_get:
            mock_get.return_value.status_code = 200  # Mock the status code
            mock_get.return_value.json.return_value = json.loads(
                valid_uei_results
            )  # Mock the json
            results = get_uei_info_from_sam_gov(uei=test_uei)

            self.assertTrue(results["valid"])
            self.assertRaises(KeyError, lambda: results["errors"])
            self.assertEqual(
                results["response"],
                json.loads(valid_uei_results)["entityData"][0],
            )

        # Invalid Status Code
        with patch("api.uei.requests.get") as mock_get:
            mock_get.return_value.status_code = 400  # Mock the status code
            results = get_uei_info_from_sam_gov(uei=test_uei)

            self.assertFalse(results["valid"])
            self.assertTrue(results["errors"])
            self.assertEquals(
                results["errors"],
                ["SAM.gov API response status code invalid: 400"],
            )

        # Timeout
        with patch("api.uei.requests.get") as mock_get:

            def bad_timeout(*args, **kwds):
                raise requests.exceptions.Timeout

            mock_get.side_effect = bad_timeout
            results = get_uei_info_from_sam_gov(uei=test_uei)

            self.assertFalse(results["valid"])
            self.assertTrue(results["errors"])
            self.assertEquals(results["errors"], ["SAM.gov API timeout"])

        # TooManyRedirects
        with patch("api.uei.requests.get") as mock_get:

            def bad_redirects(*args, **kwds):
                raise requests.exceptions.TooManyRedirects

            mock_get.side_effect = bad_redirects
            results = get_uei_info_from_sam_gov(uei=test_uei)

            self.assertFalse(results["valid"])
            self.assertTrue(results["errors"])
            self.assertEquals(
                results["errors"], ["SAM.gov API error - too many redirects"]
            )

        # RequestException
        with patch("api.uei.requests.get") as mock_get:

            def bad_reqexception(*args, **kwds):
                raise requests.exceptions.RequestException

            mock_get.side_effect = bad_reqexception
            results = get_uei_info_from_sam_gov(uei=test_uei)

            self.assertFalse(results["valid"])
            self.assertTrue(results["errors"])
            self.assertEquals(
                results["errors"],
                ["Unable to make SAM.gov API request, error: "],
            )

        # UEI registrationStatus not active
        with patch("api.uei.requests.get") as mock_get:
            mock_get.return_value.status_code = 200  # Mock the status code
            mock_get.return_value.json.return_value = json.loads(
                invalid_uei_results
            )  # Mock the json
            results = get_uei_info_from_sam_gov(uei=test_uei)

            self.assertFalse(results["valid"])
            self.assertTrue(results["errors"])

        # No matching UEI's found
        with patch("api.uei.requests.get") as mock_get:
            mock_get.return_value.status_code = 200  # Mock the status code
            mock_get.return_value.json.return_value = json.loads(
                missing_uei_results
            )  # Mock the json
            results = get_uei_info_from_sam_gov(uei=test_uei)

            self.assertFalse(results["valid"])
            self.assertTrue(results["errors"])
            self.assertEquals(
                results["errors"],
                ["UEI was not found in SAM.gov"],
            )

        # Invalid number of SAM.gov entries
        with patch("api.uei.requests.get") as mock_get:
            mock_get.return_value.status_code = 200  # Mock the status code
            mock_get.return_value.json.return_value = json.loads(
                lying_uei_results
            )  # Mock the json

            results = get_uei_info_from_sam_gov(uei=test_uei)

            self.assertFalse(results["valid"])
            self.assertTrue(results["errors"])
            self.assertEquals(
                results["errors"],
                ["SAM.gov invalid number of entries"],
            )

        # Invalid number of SAM.gov entries
        with patch("api.uei.requests.get") as mock_get:
            mock_get.return_value.status_code = 200  # Mock the status code
            mock_get.return_value.json.return_value = json.loads(
                misshapen_uei_results
            )  # Mock the json

            results = get_uei_info_from_sam_gov(uei=test_uei)

            self.assertFalse(results["valid"])
            self.assertTrue(results["errors"])
            self.assertEquals(
                results["errors"],
                ["SAM.gov unexpected JSON shape"],
            )

        # Inactive entry
        with patch("api.uei.requests.get") as mock_get:
            mock_get.return_value.status_code = 200  # Mock the status code
            mock_get.return_value.json.return_value = json.loads(
                inactive_uei_results
            )  # Mock the json

            results = get_uei_info_from_sam_gov(uei=test_uei)

            self.assertFalse(results["valid"])
            self.assertTrue(results["errors"])
            self.assertEquals(
                results["errors"],
                ["UEI is not listed as active from SAM.gov response data"],
            )
