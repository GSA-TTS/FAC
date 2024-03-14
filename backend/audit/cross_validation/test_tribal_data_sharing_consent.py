from django.test import TestCase

from audit.models import SingleAuditChecklist

from .errors import (
    err_missing_tribal_data_sharing_consent,
    err_unexpected_tribal_data_sharing_consent,
)
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

        shaped_sac_missing = shaped_sac | {"tribal_data_consent": {}}

        validation_missing = tribal_data_sharing_consent(shaped_sac_missing)

        self.assertEqual(
            validation_missing, [{"error": err_missing_tribal_data_sharing_consent()}]
        )

        falses = {
            "tribal_data_consent": {
                "tribal_authorization_certifying_official_title": False,
                "is_tribal_information_authorized_to_be_public": False,
                "tribal_authorization_certifying_official_name": False,
            }
        }

        shaped_sac_falses = shaped_sac | falses
        validation_falses = tribal_data_sharing_consent(shaped_sac_falses)

        self.assertEqual(
            validation_falses, [{"error": err_missing_tribal_data_sharing_consent()}]
        )

        not_even_wrong = {
            "tribal_data_consent": {
                "tribal_authorization_certifying_official_title": False,
                "is_tribal_information_authorized_to_be_public": "string",
                "tribal_authorization_certifying_official_name": False,
            }
        }
        shaped_sac_not_even_wrong = shaped_sac | not_even_wrong
        validation_not_even_wrong = tribal_data_sharing_consent(
            shaped_sac_not_even_wrong
        )

        self.assertEqual(
            validation_not_even_wrong,
            [{"error": err_missing_tribal_data_sharing_consent()}],
        )

    def test_tribal_org_with_consent(self):
        """SACs for tribal orders should pass this validation if there is a completed data sharing consent form"""
        sac = baker.make(SingleAuditChecklist)

        sac.general_information = {"user_provided_organization_type": "tribal"}

        sac.tribal_data_consent = {
            "tribal_authorization_certifying_official_title": "Assistant Regional Manager",
            "is_tribal_information_authorized_to_be_public": True,
            "tribal_authorization_certifying_official_name": "A. Human",
        }

        shaped_sac = sac_validation_shape(sac)

        validation_result = tribal_data_sharing_consent(shaped_sac)

        self.assertEqual(validation_result, [])

    def test_non_tribal_org_with_consent(self):
        """SACS for non-tribal orgs should not pass if they have filled out a tribal consent form"""
        sac = baker.make(SingleAuditChecklist)

        sac.tribal_data_consent = {
            "tribal_authorization_certifying_official_title": "Assistant Regional Manager",
            "is_tribal_information_authorized_to_be_public": True,
            "tribal_authorization_certifying_official_name": "A. Human",
        }

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

                self.assertEqual(
                    validation_result,
                    [{"error": err_unexpected_tribal_data_sharing_consent()}],
                )
