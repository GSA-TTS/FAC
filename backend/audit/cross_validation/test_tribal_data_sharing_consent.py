from django.test import TestCase

from audit.models import SingleAuditChecklist

from .errors import err_missing_tribal_data_sharing_consent
from .tribal_data_sharing_consent import tribal_data_sharing_consent
from .sac_validation_shape import sac_validation_shape

from model_bakery import baker


class TribalDataSharingConsentTests(TestCase):
    def test_non_tribal_org(self):
        """SACs for non-tribal orgs should pass this validation"""
        sac = baker.make(SingleAuditChecklist)

        non_tribal_org_types = [
            "state",
            "local",
            "higher-ed",
            "non-profit",
            "unknown",
            "none",
        ]

        for type in non_tribal_org_types:
            with self.subTest():
                sac.general_information = {"user_provided_organization_type": type}

                shaped_sac = sac_validation_shape(sac)

                validation_result = tribal_data_sharing_consent(shaped_sac)

                self.assertEqual(validation_result, [])

    def test_tribal_org_without_consent(self):
        """SACs for tribal orgs should not pass this validation if there is not a completed data sharing consent form"""
        sac = baker.make(SingleAuditChecklist)

        sac.general_information = {"user_provided_organization_type": "tribal"}

        shaped_sac = sac_validation_shape(sac)

        validation_result = tribal_data_sharing_consent(shaped_sac)

        self.assertEqual(
            validation_result, [{"error": err_missing_tribal_data_sharing_consent()}]
        )
