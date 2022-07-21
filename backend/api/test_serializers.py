import json
from unittest import TestCase

from unittest.mock import patch
from django.test import SimpleTestCase

from api.test_uei import valid_uei_results
from api.serializers import (
    EligibilitySerializer,
    UEISerializer,
    AuditeeInfoSerializer,
    AccessSerializer,
    AccessAndSubmissionSerializer,
)
from audit.models import User


class EligibilityStepTests(SimpleTestCase):
    def test_valid_eligibility(self):
        valid = {
            "is_usa_based": True,
            "met_spending_threshold": True,
            "user_provided_organization_type": "state",
        }
        self.assertTrue(EligibilitySerializer(data=valid).is_valid())

    def test_invalid_eligibility(self):
        invalid = {
            "is_usa_based": False,
            "met_spending_threshold": True,
            "user_provided_organization_type": "state",
        }
        self.assertFalse(EligibilitySerializer(data=invalid).is_valid())

    def test_empty_payload(self):
        empty = {}
        self.assertFalse(EligibilitySerializer(data=empty).is_valid())

    def test_invalid_user_provided_organization(self):
        wrong_choice = {
            "is_usa_based": True,
            "met_spending_threshold": True,
            "user_provided_organization_type": "not a valid type",
        }
        self.assertFalse(EligibilitySerializer(data=wrong_choice).is_valid())

    def test_did_not_meet_threshold(self):
        did_not_meet_threshold = {
            "is_usa_based": True,
            "met_spending_threshold": False,
            "user_provided_organization_type": "state",
        }
        self.assertFalse(EligibilitySerializer(data=did_not_meet_threshold).is_valid())

    def test_none_organization_type(self):
        organization_type_none = {
            "is_usa_based": True,
            "met_spending_threshold": False,
            "user_provided_organization_type": "none",
        }
        self.assertFalse(EligibilitySerializer(data=organization_type_none).is_valid())


class UEIValidatorStepTests(SimpleTestCase):
    def test_valid_uei_payload(self):
        """
        UEI should meet UEI Technical Specifications defined in the UEI validator
        """
        valid = {"auditee_uei": "ZQGGHJH74DW7"}

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

    def test_invalid_uei_payload(self):
        """
        UEI should meet UEI Technical Specifications defined in the UEI validator
        """
        invalid = {"auditee_uei": "0000000000OI*"}

        # Invalid
        self.assertFalse(UEISerializer(data=invalid).is_valid())


class AuditeeInfoStepTests(SimpleTestCase):
    def test_valid_auditee_info_with_uei(self):
        valid_with_uei = {
            "auditee_uei": "ZQGGHJH74DW7",
            "auditee_fiscal_period_start": "2021-01-01",
            "auditee_fiscal_period_end": "2021-12-31",
            "auditee_name": "FacCo, Inc.",
        }
        self.assertTrue(AuditeeInfoSerializer(data=valid_with_uei).is_valid())

    def test_valid_auditee_info_without_uei(self):
        valid_missing_uei = {
            "auditee_fiscal_period_start": "2021-01-01",
            "auditee_fiscal_period_end": "2021-12-31",
            "auditee_name": "FacCo, Inc.",
        }
        self.assertTrue(AuditeeInfoSerializer(data=valid_missing_uei).is_valid())

    def test_valid_auditee_info_without_name(self):
        valid_missing_name = {
            "auditee_uei": "ZQGGHJH74DW7",
            "auditee_fiscal_period_start": "2021-01-01",
            "auditee_fiscal_period_end": "2021-12-31",
        }
        self.assertTrue(AuditeeInfoSerializer(data=valid_missing_name).is_valid())

    def test_empty_payload(self):
        empty = {}
        self.assertFalse(AuditeeInfoSerializer(data=empty).is_valid())

    def test_missing_fiscal_start_date(self):
        missing_start = {
            "auditee_uei": "ZQGGHJH74DW7",
            "auditee_fiscal_period_end": "2021-12-31",
            "auditee_name": "FacCo, Inc.",
        }
        self.assertFalse(AuditeeInfoSerializer(data=missing_start).is_valid())

    def test_missing_fiscal_end_date(self):
        missing_end = {
            "auditee_uei": "ZQGGHJH74DW7",
            "auditee_fiscal_period_start": "2021-01-01",
            "auditee_name": "FacCo, Inc.",
        }
        self.assertFalse(AuditeeInfoSerializer(data=missing_end).is_valid())

    def test_missing_fiscal_start_and_end_dates(self):
        missing_start_and_end = {"auditee_name": "FacCo, Inc."}
        self.assertFalse(AuditeeInfoSerializer(data=missing_start_and_end).is_valid())


class AccessSerializerTests(TestCase):
    def test_valid_access(self):
        data = {
            "role": "auditee_contact",
            "email": "firstname.lastname@gsa.gov",
            "user": User.objects.first(),
        }
        self.assertTrue(AccessSerializer(data=data).is_valid())

    def test_invalid_role(self):
        data = {
            "role": "this is a role that's not really a role",
            "email": "firstname.lastname@gsa.gov",
            "user": User.objects.first(),
        }
        self.assertFalse(AccessSerializer(data=data).is_valid())

    def test_invalid_email(self):
        data = {
            "role": "auditee_contact",
            "email": "this is not an email address",
            "user": User.objects.first(),
        }
        self.assertFalse(AccessSerializer(data=data).is_valid())

    def test_invalid_user(self):
        data = {
            "role": "auditee_contact",
            "email": "firstname.lastname@gsa.gov",
            "user": "Robert McRobertson",
        }
        self.assertFalse(AccessSerializer(data=data).is_valid())


class AccessAndSubmissionStepTests(TestCase):
    def test_valid_payload_with_one_contact(self):
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
        self.assertTrue(AccessAndSubmissionSerializer(data=valid1).is_valid())

    def test_valid_payload_with_two_contacts(self):
        valid2 = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com", "d@d.com"],
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }
        self.assertTrue(AccessAndSubmissionSerializer(data=valid2).is_valid())

    def test_empty_payload(self):
        empty = {}
        self.assertFalse(AccessAndSubmissionSerializer(data=empty).is_valid())

    def test_missing_certifying_auditee(self):
        missing_cert_auditee = {
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com", "d@d.com"],
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }
        self.assertFalse(
            AccessAndSubmissionSerializer(data=missing_cert_auditee).is_valid()
        )

    def test_missing_certifying_auditor(self):
        missing_cert_auditor = {
            "certifying_auditee_contact": "a@a.com",
            "auditor_contacts": ["c@c.com", "d@d.com"],
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }
        self.assertFalse(
            AccessAndSubmissionSerializer(data=missing_cert_auditor).is_valid()
        )

    def test_missing_auditor_contacts(self):
        missing_auditor_contacts = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }
        self.assertFalse(
            AccessAndSubmissionSerializer(data=missing_auditor_contacts).is_valid()
        )

    def test_missing_auditee_contacts(self):
        missing_auditee_contacts = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com", "d@d.com"],
        }
        self.assertFalse(
            AccessAndSubmissionSerializer(data=missing_auditee_contacts).is_valid()
        )

    def test_auditee_contacts_not_in_a_list(self):
        auditee_contacts_not_list = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": "c@c.com",
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }
        self.assertFalse(
            AccessAndSubmissionSerializer(data=auditee_contacts_not_list).is_valid()
        )

    def test_auditor_contacts_not_in_a_list(self):
        auditor_contacts_not_list = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com", "d@d.com"],
            "auditee_contacts": "e@e.com",
        }
        self.assertFalse(
            AccessAndSubmissionSerializer(data=auditor_contacts_not_list).is_valid()
        )

    def test_certifying_auditee_not_valid_email(self):
        cert_auditee_not_valid_email = {
            "certifying_auditee_contact": "this is not an email",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com", "d@d.com"],
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }
        self.assertFalse(
            AccessAndSubmissionSerializer(data=cert_auditee_not_valid_email).is_valid()
        )

    def test_certifying_auditor_not_valid_email(self):
        cert_auditor_not_valid_email = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "this is not an email",
            "auditor_contacts": ["c@c.com", "d@d.com"],
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }
        self.assertFalse(
            AccessAndSubmissionSerializer(data=cert_auditor_not_valid_email).is_valid()
        )

    def test_auditor_list_not_all_valid_emails(self):
        auditor_not_all_valid_emails = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com", "this is not an email", "d@d.com"],
            "auditee_contacts": ["e@e.com", "f@f.com"],
        }
        self.assertFalse(
            AccessAndSubmissionSerializer(data=auditor_not_all_valid_emails).is_valid()
        )

    def test_auditee_list_not_all_valid_emails(self):
        auditee_not_all_valid_emails = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com", "d@d.com"],
            "auditee_contacts": ["e@e.com", "this is not an email", "f@f.com"],
        }
        self.assertFalse(
            AccessAndSubmissionSerializer(data=auditee_not_all_valid_emails).is_valid()
        )
