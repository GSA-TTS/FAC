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
ACCESS_PATH = reverse("access")

VALID_AUDITEE_INFO_DATA = {
    "uei": "ABC123DEF456",
    "auditee_fiscal_period_start": "2021-01-01",
    "auditee_fiscal_period_end": "2022-01-01",
    "auditee_name": "Tester",
}
VALID_ELIGIBILITY_DATA = {
    "is_usa_based": True,
    "met_spending_threshold": True,
    "user_provided_organization_type": "state",
}
VALID_ACCESS_DATA = [
    {"role": "auditee_contact", "email": "a@a.com"},
    {"role": "auditor_contact", "email": "c@c.com"},
]


class EligibilityViewTests(TestCase):
    INELIGIBLE = {
        "is_usa_based": False,
        "met_spending_threshold": True,
        "user_provided_organization_type": "state",
    }

    def test_auth_required(self):
        """Unauthenticated requests return unauthorized response"""
        client = APIClient()
        response = client.post(
            ELIGIBILITY_PATH, VALID_ELIGIBILITY_DATA, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_success_and_failure(self):
        """
        An authenticated request receives an eligible response and an ineligible response
        """
        client = APIClient()
        user = baker.make(User)
        client.force_authenticate(user=user)

        response = client.post(
            ELIGIBILITY_PATH, VALID_ELIGIBILITY_DATA, format="json"
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["eligible"], True)

        response = client.post(
            ELIGIBILITY_PATH, self.INELIGIBLE, format="json"
        )
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["eligible"], False)


class UEIValidationViewTests(TestCase):
    PATH = reverse("uei-validation")
    SUCCESS = {"uei": "ZQGGHJH74DW7"}
    INELIGIBLE = {"uei": "000000000OI*"}

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
        self.assertEqual(data["next"], ACCESS_PATH)
        self.assertEqual(
            self.user.profile.entry_form_data,
            VALID_ELIGIBILITY_DATA | VALID_AUDITEE_INFO_DATA,
        )


class AccessTests(TestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_missing_expected_form_data_from_prior_steps(self):
        """Return an error and point to Eligibility step if we're missing data from any prior step"""
        # Missing Eligibility data
        response = self.client.post(
            ACCESS_PATH, VALID_ACCESS_DATA, format="json"
        )
        data = response.json()
        self.assertEqual(data["next"], ELIGIBILITY_PATH)
        self.assertTrue(data["errors"])

        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()

        # Have eligibility, but missing auditee info data
        response = self.client.post(
            ACCESS_PATH, VALID_ACCESS_DATA, format="json"
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
            ACCESS_PATH, VALID_ACCESS_DATA, format="json"
        )
        data = response.json()

        sac = SingleAuditChecklist.objects.get(id=data["sac_id"])
        self.assertEqual(
            sac.users.get(role="auditee_contact").email, "a@a.com"
        )
        self.assertEqual(
            sac.users.get(role="auditor_contact").email, "c@c.com"
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
        response = self.client.post(
            ELIGIBILITY_PATH, eligibility_info, format="json"
        )
        data = response.json()
        next_step = data["next"]

        # Submit auditee info
        response = self.client.post(
            next_step, VALID_AUDITEE_INFO_DATA, format="json"
        )
        data = response.json()
        next_step = data["next"]

        # Submit Access details
        access_data = [
            {"role": "auditee_contact", "email": "test@example.com"},
            {"role": "auditor_contact", "email": "testerc@example.com"},
        ]
        response = self.client.post(next_step, access_data, format="json")
        data = response.json()
        sac = SingleAuditChecklist.objects.get(id=data["sac_id"])
        self.assertEqual(sac.submitted_by, self.user)
        self.assertEqual(sac.uei, "ABC123DEF456")
