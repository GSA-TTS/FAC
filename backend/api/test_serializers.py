import json

from unittest.mock import patch
from django.test import SimpleTestCase

from api.test_uei import valid_uei_results
from api.serializers import (
    EligibilitySerializer,
    UEISerializer,
    AuditeeInfoSerializer,
    AccessAndSubmissionSerializer,
)


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


class AuditeeInfoStepTests(SimpleTestCase):
    def test_serializer_validation(self):
        """
        Auditee Name, Fiscal Period start/end are all required
        Auditee UEI is optional
        """
        valid_with_uei = {
            "auditee_uei": "ZQGGHJH74DW7",
            "auditee_fiscal_period_start": "2021-01-01",
            "auditee_fiscal_period_end": "2021-12-31",
            "auditee_name": "FacCo, Inc.",
        }
        valid_missing_uei = {
            "auditee_fiscal_period_start": "2021-01-01",
            "auditee_fiscal_period_end": "2021-12-31",
            "auditee_name": "FacCo, Inc.",
        }
        valid_missing_name = {
            "auditee_uei": "ZQGGHJH74DW7",
            "auditee_fiscal_period_start": "2021-01-01",
            "auditee_fiscal_period_end": "2021-12-31",
        }

        empty = {}
        missing_start = {
            "auditee_uei": "ZQGGHJH74DW7",
            "auditee_fiscal_period_end": "2021-12-31",
            "auditee_name": "FacCo, Inc.",
        }
        missing_end = {
            "auditee_uei": "ZQGGHJH74DW7",
            "auditee_fiscal_period_start": "2021-01-01",
            "auditee_name": "FacCo, Inc.",
        }
        missing_start_and_end = {"auditee_name": "FacCo, Inc."}

        self.assertFalse(AuditeeInfoSerializer(data=empty).is_valid())
        self.assertFalse(AuditeeInfoSerializer(data=missing_start).is_valid())
        self.assertFalse(AuditeeInfoSerializer(data=missing_end).is_valid())
        self.assertFalse(AuditeeInfoSerializer(data=missing_start_and_end).is_valid())
        self.assertTrue(AuditeeInfoSerializer(data=valid_with_uei).is_valid())
        self.assertTrue(AuditeeInfoSerializer(data=valid_missing_uei).is_valid())
        self.assertTrue(AuditeeInfoSerializer(data=valid_missing_name).is_valid())


class AccessAndSubmissionStepTests(SimpleTestCase):
    def test_serializer_validation(self):
        """
        Auditee Name, Fiscal Period start/end are all required
        Auditee UEI is optional
        """
        valid1 = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com"],
            "auditee_contacts": ["e@e.com"],
        }
        valid2 = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com", "d@d.com"],
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }

        empty = {}
        missing_cert_auditee = {
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com", "d@d.com"],
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }
        missing_cert_auditor = {
            "certifying_auditee_contact": "a@a.com",
            "auditor_contacts": ["c@c.com", "d@d.com"],
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }
        missing_auditor_contacts = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }
        missing_auditee_contacts = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com", "d@d.com"],
        }
        auditee_contacts_not_list = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": "c@c.com",
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }
        auditor_contacts_not_list = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com", "d@d.com"],
            "auditee_contacts": "e@e.com",
        }
        cert_auditee_not_valid_email = {
            "certifying_auditee_contact": "this is not an email",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com", "d@d.com"],
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }
        cert_auditor_not_valid_email = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "this is not an email",
            "auditor_contacts": ["c@c.com", "d@d.com"],
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }
        auditor_not_all_valid_emails = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com", "this is not an email", "d@d.com"],
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }
        auditee_not_all_valid_emails = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com", "d@d.com"],
            "auditee_contacts": ["e@e.com", "this is not an email", "f@f.com"],
        }

        self.assertFalse(AccessAndSubmissionSerializer(data=empty).is_valid())
        self.assertFalse(
            AccessAndSubmissionSerializer(data=missing_cert_auditee).is_valid()
        )
        self.assertFalse(
            AccessAndSubmissionSerializer(data=missing_cert_auditor).is_valid()
        )
        self.assertFalse(
            AccessAndSubmissionSerializer(data=missing_auditee_contacts).is_valid()
        )
        self.assertFalse(
            AccessAndSubmissionSerializer(data=missing_auditor_contacts).is_valid()
        )
        self.assertFalse(
            AccessAndSubmissionSerializer(data=auditee_contacts_not_list).is_valid()
        )
        self.assertFalse(
            AccessAndSubmissionSerializer(data=auditor_contacts_not_list).is_valid()
        )
        self.assertFalse(
            AccessAndSubmissionSerializer(data=cert_auditee_not_valid_email).is_valid()
        )
        self.assertFalse(
            AccessAndSubmissionSerializer(data=cert_auditor_not_valid_email).is_valid()
        )
        self.assertFalse(
            AccessAndSubmissionSerializer(data=auditor_not_all_valid_emails).is_valid()
        )
        self.assertFalse(
            AccessAndSubmissionSerializer(data=auditee_not_all_valid_emails).is_valid()
        )
        self.assertTrue(AccessAndSubmissionSerializer(data=valid1).is_valid())
        self.assertTrue(AccessAndSubmissionSerializer(data=valid2).is_valid())
