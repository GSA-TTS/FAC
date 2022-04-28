import json

from django.test import SimpleTestCase
from unittest.mock import patch

from .serializers import EligibilitySerializer, UEISerializer


valid_uei_results = '{"totalRecords": 1, "entityData": [{"entityRegistration": {"samRegistered": "Yes", "ueiSAM": "ZQGGHJH74DW7", "entityEFTIndicator": null, "cageCode": "855J5", "dodaac": null, "legalBusinessName": "INTERNATIONAL BUSINESS MACHINES CORPORATION", "dbaName": null, "purposeOfRegistrationCode": "Z2", "purposeOfRegistrationDesc": "All Awards", "registrationStatus": "Inactive", "evsSource": "D&B", "registrationDate": "2018-07-24", "lastUpdateDate": "2022-03-29", "registrationExpirationDate": "2022-02-06", "activationDate": "2020-08-13", "ueiStatus": "Active", "ueiExpirationDate": null, "ueiCreationDate": "2020-05-01", "publicDisplayFlag": "Y", "exclusionStatusFlag": "N", "exclusionURL": null, "dnbOpenData": null}}], "links": {"selfLink": "https://api.sam.gov/entity-information/v3/entities?api_key=REPLACE_WITH_API_KEY&ueiSAM=ZQGGHJH74DW7&includeSections=entityRegistration&page=0&size=10"}}'


class EligibilityStepTests(SimpleTestCase):

    def test_serializer_validation(self):
        """
            IS_USA_BASE and MET_SPENDING_THRESHOLD must be True
            USER_PROVIDED_ORGANIZATION_TYPE must be one of: audit.SingleAuditChecklist.USER_PROVIDED_ORGANIZATION_TYPE
        """
        valid = {'is_usa_based': True, 'met_spending_threshold': True, 'user_provided_organization_type': 'state'}
        invalid = {'is_usa_based': False, 'met_spending_threshold': True, 'user_provided_organization_type': 'state'}
        empty = {}
        wrong_choice = {'is_usa_based': True, 'met_spending_threshold': True, 'user_provided_organization_type': 'not a valid type'}
        did_not_meet_threshold = {'is_usa_based': True, 'met_spending_threshold': False, 'user_provided_organization_type': 'state'}

        self.assertFalse(EligibilitySerializer(data=invalid).is_valid())
        self.assertFalse(EligibilitySerializer(data=empty).is_valid())
        self.assertFalse(EligibilitySerializer(data=wrong_choice).is_valid())
        self.assertFalse(EligibilitySerializer(data=did_not_meet_threshold).is_valid())
        self.assertTrue(EligibilitySerializer(data=valid).is_valid())


class UEIValidatorStepTests(SimpleTestCase):

    def test_serializer_validation(self):
        """
            UEI should meet UEI Technical Specifications defined in the UEI validator
        """
        valid = {'uei': 'ZQGGHJH74DW7'}
        invalid = {'uei': '0000000000OI*'}

        # Invalid
        self.assertFalse(UEISerializer(data=invalid).is_valid())

        # Valid
        with patch('api.utils.requests.get') as mock_get:
            mock_get.return_value.status_code = 200 # Mock the status code
            mock_get.return_value.json.return_value = json.loads(valid_uei_results) # Mock the json
            
            self.assertTrue(UEISerializer(data=valid).is_valid())
