import json

from unittest.mock import patch
from django.test import TestCase

from .utils import get_uei_info_from_sam_gov


fake_uei_results = '{"totalRecords": 1, "entityData": [{"entityRegistration": {"samRegistered": "Yes", "ueiSAM": "ZQGGHJH74DW7", "entityEFTIndicator": null, "cageCode": "855J5", "dodaac": null, "legalBusinessName": "INTERNATIONAL BUSINESS MACHINES CORPORATION", "dbaName": null, "purposeOfRegistrationCode": "Z2", "purposeOfRegistrationDesc": "All Awards", "registrationStatus": "Inactive", "evsSource": "D&B", "registrationDate": "2018-07-24", "lastUpdateDate": "2022-03-29", "registrationExpirationDate": "2022-02-06", "activationDate": "2020-08-13", "ueiStatus": "Active", "ueiExpirationDate": null, "ueiCreationDate": "2020-05-01", "publicDisplayFlag": "Y", "exclusionStatusFlag": "N", "exclusionURL": null, "dnbOpenData": null}}], "links": {"selfLink": "https://api.sam.gov/entity-information/v3/entities?api_key=REPLACE_WITH_API_KEY&ueiSAM=ZQGGHJH74DW7&includeSections=entityRegistration&page=0&size=10"}}'


class UtilsTesting(TestCase):

    def test_get_uei_info_from_sam_gov(self):
        """
        Tests UEI validation
        """
        test_uei = "ZQGGHJH74DW7"
        invalid_uei = "ABC123DEF456"

        # Valid
        with patch('api.utils.requests.get') as mock_get:
            mock_get.return_value.status_code = 200 # Mock the status code
            mock_get.return_value.json = fake_uei_results # Mock the json

            self.assertEqual(get_uei_info_from_sam_gov(uei=test_uei), json.loads(fake_uei_results)['entityData'][0])

        # Invalid Status Code
        with patch('api.utils.requests.get') as mock_get:
            mock_get.return_value.status_code = 400  # Mock the status code

            self.assertRaises(Exception, get_uei_info_from_sam_gov, test_uei)

        # Non-matching UEI
        with patch('api.utils.requests.get') as mock_get:
            mock_get.return_value.status_code = 200 # Mock the status code
            mock_get.return_value.json = fake_uei_results # Mock the json

            self.assertRaises(Exception, get_uei_info_from_sam_gov, invalid_uei)

        # More tests...
