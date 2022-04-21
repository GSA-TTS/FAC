from django.test import SimpleTestCase
from .serializers import EligibilitySerializer, UEISerializer


class EligibilityStepTests(SimpleTestCase):

    def test_serializer_validation(self):
        """
            IS_USA_BASE and MET_SPENDING_THRESHOLD must bge True
            USER_PROVIDED_ORGANIZATION_TYPE must be one of: audit.SingleAuditChecklist.USER_PROVIDED_ORGANIZATION_TYPE
        """
        valid = {'is_usa_based': True, 'met_spending_threshold': True, 'user_provided_organization_type': 'state'}
        invalid = {'is_usa_based': False, 'met_spending_threshold': True, 'user_provided_organization_type': 'state'}
        empty = {}
        wrong_choice = {'is_usa_based': True, 'met_spending_threshold': True, 'user_provided_organization_type': 'not a valid type'}

        self.assertFalse(EligibilitySerializer(data=invalid).is_valid())
        self.assertFalse(EligibilitySerializer(data=empty).is_valid())
        self.assertFalse(EligibilitySerializer(data=wrong_choice).is_valid())
        self.assertTrue(EligibilitySerializer(data=valid).is_valid())


class UEIValidatorStepTests(SimpleTestCase):

    def test_serializer_validation(self):
        """
            UEI should meet UEI Technical Specifications defined in the UEI validator
        """
        valid = {'uei': 'ABC123DEF456'}
        invalid = {'uei': '0000000000OI*'}

        self.assertFalse(UEISerializer(data=invalid).is_valid())
        self.assertTrue(UEISerializer(data=valid).is_valid())
