from django.test import TestCase

from .audit_validation_shape import audit_validation_shape
from .errors import (
    err_missing_tribal_data_sharing_consent,
    err_unexpected_tribal_data_sharing_consent,
)
from .tribal_data_sharing_consent import tribal_data_sharing_consent

from model_bakery import baker

from ..models import Audit


class TribalDataSharingConsentTests(TestCase):
    def test_non_tribal_org(self):
        """SACs for non-tribal orgs should pass this validation"""
        audit = baker.make(Audit, audit={}, version=0)

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
                audit.audit.update(
                    {"general_information": {"user_provided_organization_type": type}}
                )

                shaped_audit = audit_validation_shape(audit)

                validation_result = tribal_data_sharing_consent(shaped_audit)

                self.assertEqual(validation_result, [])

    def test_tribal_org_without_consent(self):
        """SACs for tribal orgs should not pass this validation if there is not a completed data sharing consent form"""
        audit_data = {
            "general_information": {"user_provided_organization_type": "tribal"}
        }
        audit = baker.make(Audit, audit=audit_data, version=0)

        shaped_audit = audit_validation_shape(audit)

        validation_result = tribal_data_sharing_consent(shaped_audit)

        self.assertEqual(
            validation_result, [{"error": err_missing_tribal_data_sharing_consent()}]
        )

        shaped_audit_missing = shaped_audit | {"tribal_data_consent": {}}

        validation_missing = tribal_data_sharing_consent(shaped_audit_missing)

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

        shaped_audit_falses = shaped_audit | falses
        validation_falses = tribal_data_sharing_consent(shaped_audit_falses)

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
        shaped_audit_not_even_wrong = shaped_audit | not_even_wrong
        validation_not_even_wrong = tribal_data_sharing_consent(
            shaped_audit_not_even_wrong
        )

        self.assertEqual(
            validation_not_even_wrong,
            [{"error": err_missing_tribal_data_sharing_consent()}],
        )

    def test_tribal_org_with_consent(self):
        """SACs for tribal orders should pass this validation if there is a completed data sharing consent form"""
        audit_data = {
            "general_information": {"user_provided_organization_type": "tribal"},
            "tribal_data_consent": {
                "tribal_authorization_certifying_official_title": "Assistant Regional Manager",
                "is_tribal_information_authorized_to_be_public": True,
                "tribal_authorization_certifying_official_name": "A. Human",
            },
        }
        audit = baker.make(Audit, audit=audit_data, version=0)

        shaped_audit = audit_validation_shape(audit)

        validation_result = tribal_data_sharing_consent(shaped_audit)

        self.assertEqual(validation_result, [])

    def test_non_tribal_org_with_consent(self):
        """SACS for non-tribal orgs should not pass if they have filled out a tribal consent form"""
        audit_data = {
            "tribal_data_consent": {
                "tribal_authorization_certifying_official_title": "Assistant Regional Manager",
                "is_tribal_information_authorized_to_be_public": True,
                "tribal_authorization_certifying_official_name": "A. Human",
            }
        }
        audit = baker.make(Audit, audit=audit_data, version=0)

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
                audit.audit.update(
                    {"general_information": {"user_provided_organization_type": type}}
                )

                shaped_audit = audit_validation_shape(audit)

                validation_result = tribal_data_sharing_consent(shaped_audit)

                self.assertEqual(
                    validation_result,
                    [{"error": err_unexpected_tribal_data_sharing_consent()}],
                )
