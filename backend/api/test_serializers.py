from django.test import SimpleTestCase
from .serializers import EligibilitySerializer


class EligibilityStepTests(SimpleTestCase):

    def test_serializer_validation(self):
        """
            IS_USA_BASE and MET_SPENDING_THRESHOLD must bge True
            ORGANIZATION_TYPE must be one of: audit.SingleAuditChecklist.ORGANIZATION_TYPE
        """
        valid = {'is_usa_based': True, 'met_spending_threshold': True, 'organization_type': 'state'}
        invalid = {'is_usa_based': False, 'met_spending_threshold': True, 'organization_type': 'state'}
        empty = {}
        wrong_choice = {'is_usa_based': True, 'met_spending_threshold': True, 'organization_type': 'not a valid type'}

        self.assertFalse(EligibilitySerializer(data=invalid).is_valid())
        self.assertFalse(EligibilitySerializer(data=empty).is_valid())
        self.assertFalse(EligibilitySerializer(data=wrong_choice).is_valid())
        self.assertTrue(EligibilitySerializer(data=valid).is_valid())
