import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

from api.test_uei import valid_uei_results
from audit.models import SingleAuditChecklist

User = get_user_model()

ELIGIBILITY_PATH = reverse("eligibility")
AUDITEE_INFO_PATH = reverse("auditee-info")
ACCESS_AND_SUBMISSION_PATH = reverse("accessandsubmission")

VALID_AUDITEE_INFO_DATA = {
    "auditee_uei": "ZQGGHJH74DW7",
    "auditee_fiscal_period_start": "2021-01-01",
    "auditee_fiscal_period_end": "2022-01-01",
    "auditee_name": "Tester",
}
VALID_ELIGIBILITY_DATA = {
    "is_usa_based": True,
    "met_spending_threshold": True,
    "user_provided_organization_type": "state",
}
VALID_ACCESS_AND_SUBMISSION_DATA = {
    "certifying_auditee_contact": "a@a.com",
    "certifying_auditor_contact": "b@b.com",
    "auditee_contacts": ["c@c.com"],
    "auditor_contacts": ["d@d.com"],
}


class EligibilityViewTests(TestCase):
    INELIGIBLE = {
        "is_usa_based": False,
        "met_spending_threshold": True,
        "user_provided_organization_type": "state",
    }

    def test_auth_required(self):
        """Unauthenticated requests return unauthorized response"""
        client = APIClient()
        response = client.post(ELIGIBILITY_PATH, VALID_ELIGIBILITY_DATA, format="json")
        self.assertEqual(response.status_code, 401)

    def test_success_and_failure(self):
        """
        An authenticated request receives an eligible response and an ineligible response
        """
        client = APIClient()
        user = baker.make(User)
        client.force_authenticate(user=user)

        response = client.post(ELIGIBILITY_PATH, VALID_ELIGIBILITY_DATA, format="json")
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["eligible"], True)

        response = client.post(ELIGIBILITY_PATH, self.INELIGIBLE, format="json")
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["eligible"], False)


class UEIValidationViewTests(TestCase):
    PATH = reverse("uei-validation")
    SUCCESS = {"auditee_uei": "ZQGGHJH74DW7"}
    INELIGIBLE = {"auditee_uei": "000000000OI*"}

    def test_auth_required(self):
        """Unauthenticated requests return unauthorized response"""
        client = APIClient()
        response = client.post(self.PATH, self.SUCCESS, format="json")
        self.assertEqual(response.status_code, 401)

    def test_success_and_failure(self):
        """
        An authenticated request receives an eligible response and an ineligible response
        """
        client = APIClient()
        user = baker.make(User)
        client.force_authenticate(user=user)

        # Valid
        with patch("api.uei.requests.get") as mock_get:
            mock_get.return_value.status_code = 200  # Mock the status code
            mock_get.return_value.json.return_value = json.loads(
                valid_uei_results
            )  # Mock the json

            response = client.post(self.PATH, self.SUCCESS, format="json")
            data = response.json()
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["valid"], True)

        response = client.post(self.PATH, self.INELIGIBLE, format="json")
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["valid"], False)


class AuditeeInfoTests(TestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_missing_expected_form_data_from_prior_step(self):
        """Return an error and point to Eligibility step if we're missing data from that step in the user's profile"""
        response = self.client.post(
            AUDITEE_INFO_PATH, VALID_AUDITEE_INFO_DATA, format="json"
        )
        data = response.json()
        self.assertEqual(data["next"], ELIGIBILITY_PATH)
        self.assertTrue(data["errors"])

    def test_valid_data_updates_profile(self):
        """Valid POST update user's form data stored in their profile"""
        # Add eligibility data to profile
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()

        response = self.client.post(
            AUDITEE_INFO_PATH, VALID_AUDITEE_INFO_DATA, format="json"
        )
        data = response.json()
        self.assertEqual(data["next"], ACCESS_AND_SUBMISSION_PATH)
        self.assertEqual(
            self.user.profile.entry_form_data,
            VALID_ELIGIBILITY_DATA | VALID_AUDITEE_INFO_DATA,
        )

    def test_null_auditee_uei(self):
        """
        Auditee UEI can be null
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA | {"auditee_uei": None}
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertEqual(data["next"], ACCESS_AND_SUBMISSION_PATH)
        self.assertEqual(
            self.user.profile.entry_form_data, VALID_ELIGIBILITY_DATA | input_data
        )

    def test_blank_auditee_uei(self):
        """
        Auditee UEI can be blank
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA | {"auditee_uei": ""}
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertEqual(data["next"], ACCESS_AND_SUBMISSION_PATH)
        self.assertEqual(
            self.user.profile.entry_form_data, VALID_ELIGIBILITY_DATA | input_data
        )

    def test_missing_auditee_uei(self):
        """
        Auditee UEI can be missing
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA.copy()
        del input_data["auditee_uei"]
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertEqual(data["next"], ACCESS_AND_SUBMISSION_PATH)
        self.assertEqual(
            self.user.profile.entry_form_data, VALID_ELIGIBILITY_DATA | input_data
        )

    def test_blank_auditee_name(self):
        """
        Auditee name cannot be blank
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA | {"auditee_name": ""}
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertTrue(data["errors"])

    def test_null_auditee_name(self):
        """
        Auditee name can be null
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA | {"auditee_name": None}
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertEqual(data["next"], ACCESS_AND_SUBMISSION_PATH)
        self.assertEqual(
            self.user.profile.entry_form_data, VALID_ELIGIBILITY_DATA | input_data
        )

    def test_missing_auditee_name(self):
        """
        Auditee name can be missing
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA.copy()
        del input_data["auditee_name"]
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertEqual(data["next"], ACCESS_AND_SUBMISSION_PATH)
        self.assertEqual(
            self.user.profile.entry_form_data, VALID_ELIGIBILITY_DATA | input_data
        )

    def test_missing_auditee_fiscal_period_start(self):
        """
        Auditee fiscal period start cannot be missing
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA.copy()
        del input_data["auditee_fiscal_period_start"]
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertTrue(data["errors"])

    def test_missing_auditee_fiscal_period_end(self):
        """
        Auditee fiscal period end cannot be missing
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA.copy()
        del input_data["auditee_fiscal_period_end"]
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertTrue(data["errors"])


class AccessAndSubmissionTests(TestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_missing_expected_form_data_from_prior_steps(self):
        """Return an error and point to Eligibility step if we're missing data from any prior step"""
        # Missing Eligibility data
        response = self.client.post(
            ACCESS_AND_SUBMISSION_PATH, VALID_ACCESS_AND_SUBMISSION_DATA, format="json"
        )
        data = response.json()
        self.assertEqual(data["next"], ELIGIBILITY_PATH)
        self.assertTrue(data["errors"])

        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()

        # Have eligibility, but missing auditee info data
        response = self.client.post(
            ACCESS_AND_SUBMISSION_PATH, VALID_ACCESS_AND_SUBMISSION_DATA, format="json"
        )
        data = response.json()
        self.assertEqual(data["next"], ELIGIBILITY_PATH)
        self.assertTrue(data["errors"])

    def test_valid_data_creates_SAC_and_Access(self):
        """A new SAC is created along with related Access instances"""
        # Add eligibility and Auditee Info data to profile
        self.user.profile.entry_form_data = (
            VALID_ELIGIBILITY_DATA | VALID_AUDITEE_INFO_DATA
        )
        self.user.profile.save()

        response = self.client.post(
            ACCESS_AND_SUBMISSION_PATH, VALID_ACCESS_AND_SUBMISSION_DATA, format="json"
        )
        data = response.json()

        sac = SingleAuditChecklist.objects.get(id=data["sac_id"])
        certifying_auditee_contact_access = sac.certifying_auditee_contact
        certifying_auditor_contact_access = sac.certifying_auditor_contact
        auditor_contacts_first_access = sac.auditor_contacts.first()
        auditee_contacts_first_access = sac.auditee_contacts.first()
        self.assertEqual(certifying_auditee_contact_access.email, "a@a.com")
        self.assertEqual(certifying_auditor_contact_access.email, "b@b.com")
        self.assertEqual(auditee_contacts_first_access.email, "c@c.com")
        self.assertEqual(auditor_contacts_first_access.email, "d@d.com")

    def test_invalid_eligibility_data(self):
        """
        Handle missing data.
        """
        self.user.profile.entry_form_data = (
            VALID_ELIGIBILITY_DATA | VALID_AUDITEE_INFO_DATA
        )
        self.user.profile.save()
        response = self.client.post(ACCESS_AND_SUBMISSION_PATH, {}, format="json")
        data = response.json()
        self.assertEqual(
            data.get("errors", [])["certifying_auditee_contact"][0],
            "This field is required.",
        )
        self.assertEqual(
            data.get("errors", [])["certifying_auditor_contact"][0],
            "This field is required.",
        )
        self.assertEqual(
            data.get("errors", [])["auditee_contacts"][0], "This field is required."
        )
        self.assertEqual(
            data.get("errors", [])["auditor_contacts"][0], "This field is required."
        )


class SACCreationTests(TestCase):
    """Integration tests covering all submission steps leading up to and including creation of a SingleAuditChecklist instance"""

    def setUp(self):
        self.user = baker.make(User)
        self.client = APIClient()

    def test_valid_data_across_steps_creates_an_sac(self):
        """Upon submitting valid data and following `next` responses, a new SAC is created"""
        self.client.force_authenticate(user=self.user)

        # Submit eligibility data
        eligibility_info = {
            "is_usa_based": True,
            "met_spending_threshold": True,
            "user_provided_organization_type": "state",
        }
        response = self.client.post(ELIGIBILITY_PATH, eligibility_info, format="json")
        data = response.json()
        next_step = data["next"]

        # Submit auditee info
        response = self.client.post(next_step, VALID_AUDITEE_INFO_DATA, format="json")
        data = response.json()
        next_step = data["next"]

        # Submit AccessAndSubmission details
        access_and_submission_data = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com"],
            "auditee_contacts": ["e@e.com"],
        }
        response = self.client.post(
            next_step, access_and_submission_data, format="json"
        )
        data = response.json()
        sac = SingleAuditChecklist.objects.get(id=data["sac_id"])
        self.assertEqual(sac.submitted_by, self.user)
        self.assertEqual(sac.auditee_uei, "ZQGGHJH74DW7")
        self.assertEqual(sac.submission_status, "in_progress")
