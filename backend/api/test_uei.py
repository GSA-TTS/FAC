import json

from unittest.mock import patch
from django.test import TestCase

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

            self.assertTrue(get_uei_info_from_sam_gov(uei=test_uei)["valid"])
            self.assertRaises(
                KeyError,
                lambda: get_uei_info_from_sam_gov(uei=test_uei)["errors"],
            )
            self.assertEqual(
                get_uei_info_from_sam_gov(uei=test_uei)["response"],
                json.loads(valid_uei_results)["entityData"][0],
            )

        # Invalid Status Code
        with patch("api.uei.requests.get") as mock_get:
            mock_get.return_value.status_code = 400  # Mock the status code

            self.assertFalse(get_uei_info_from_sam_gov(uei=test_uei)["valid"])
            self.assertTrue(get_uei_info_from_sam_gov(uei=test_uei)["errors"])

        # UEI registrationStatus not active
        with patch("api.uei.requests.get") as mock_get:
            mock_get.return_value.status_code = 200  # Mock the status code
            mock_get.return_value.json.return_value = json.loads(
                invalid_uei_results
            )  # Mock the json

            self.assertFalse(get_uei_info_from_sam_gov(uei=test_uei)["valid"])
            self.assertTrue(get_uei_info_from_sam_gov(uei=test_uei)["errors"])

        # No matching UEI's found
        with patch("api.uei.requests.get") as mock_get:
            mock_get.return_value.status_code = 200  # Mock the status code
            mock_get.return_value.json.return_value = json.loads(
                missing_uei_results
            )  # Mock the json

            self.assertFalse(get_uei_info_from_sam_gov(uei=test_uei)["valid"])
            self.assertTrue(get_uei_info_from_sam_gov(uei=test_uei)["errors"])
