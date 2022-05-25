import json

from unittest.mock import patch
from django.test import SimpleTestCase

from api.test_uei import valid_uei_results
from api.serializers import EligibilitySerializer, UEISerializer


class EligibilityStepTests(SimpleTestCase):
    def test_serializer_validation(self):
        """
        IS_USA_BASE and MET_SPENDING_THRESHOLD must be True
        USER_PROVIDED_ORGANIZATION_TYPE must be one of: audit.SingleAuditChecklist.USER_PROVIDED_ORGANIZATION_TYPE
        """
        valid = {
            "is_usa_based": True,
            "met_spending_threshold": True,
            "user_provided_organization_type": "state",
        }
        invalid = {
            "is_usa_based": False,
            "met_spending_threshold": True,
            "user_provided_organization_type": "state",
        }
        empty = {}
        wrong_choice = {
            "is_usa_based": True,
            "met_spending_threshold": True,
            "user_provided_organization_type": "not a valid type",
        }
        did_not_meet_threshold = {
            "is_usa_based": True,
            "met_spending_threshold": False,
            "user_provided_organization_type": "state",
        }
        organization_type_none = {
            "is_usa_based": True,
            "met_spending_threshold": False,
            "user_provided_organization_type": "none",
        }

        self.assertFalse(EligibilitySerializer(data=invalid).is_valid())
        self.assertFalse(EligibilitySerializer(data=empty).is_valid())
        self.assertFalse(EligibilitySerializer(data=wrong_choice).is_valid())
        self.assertFalse(EligibilitySerializer(data=did_not_meet_threshold).is_valid())
        self.assertFalse(EligibilitySerializer(data=organization_type_none).is_valid())
        self.assertTrue(EligibilitySerializer(data=valid).is_valid())


class UEIValidatorStepTests(SimpleTestCase):
    def test_serializer_validation(self):
        """
        UEI should meet UEI Technical Specifications defined in the UEI validator
        """
        valid = {"auditee_uei": "ZQGGHJH74DW7"}
        invalid = {"auditee_uei": "0000000000OI*"}

        # Invalid
        self.assertFalse(UEISerializer(data=invalid).is_valid())

        # Valid
        with patch("api.uei.requests.get") as mock_get:
            mock_get.return_value.status_code = 200  # Mock the status code
            mock_get.return_value.json.return_value = json.loads(
                valid_uei_results
            )  # Mock the json

            self.assertTrue(UEISerializer(data=valid).is_valid())

        # Has errors
        with patch("api.uei.requests.get") as mock_get:
            mock_get.return_value.status_code = 200  # Mock the status code
            mock_get.return_value.json.return_value = {"errors": [1, 2, 3]}
            self.assertFalse(UEISerializer(data=valid).is_valid())
