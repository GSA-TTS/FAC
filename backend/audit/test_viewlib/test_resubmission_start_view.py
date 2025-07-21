from model_bakery import baker

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from audit.models import SingleAuditChecklist
from audit.models.constants import STATUS


User = get_user_model()


class ResubmissionStartViewTests(TestCase):
    # Constants
    path_name = reverse("audit:ResubmissionStart")
    invalid_report_id = "NOT-LONG-ENOUGH"
    nonexistent_report_id = "LONGENOUGHBUTDOESNOTEXIST"
    valid_report_id = "0123-01-SOURCE-0123456789"

    # Recreated per test
    def setUp(self):
        """Setup user and client."""
        self.valid_sac = baker.make(
            SingleAuditChecklist,
            report_id=self.valid_report_id,
            submission_status=STATUS.DISSEMINATED,
        )
        self.user = baker.make(User)
        self.client = Client()

    def test_redirect_if_not_logged_in(self):
        """Test that accessing resubmission start page redirects if the user is not logged in"""
        response = self.client.get(self.path_name)
        self.assertAlmostEqual(response.status_code, 302)

    def test_invalid_report_id(self):
        """Test that an invalid report_id reloads the page with an error message."""
        self.client.force_login(user=self.user)
        response = self.client.post(
            self.path_name, {"report_id": self.invalid_report_id}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "audit/resubmission_start_form.html")
        self.assertIn("form", response.context)
        self.assertIn("too short", str(response.context["form"].errors))

    def test_nonexistent_report(self):
        """Test that a report_id for an audit that does not exist reloads the page with an error message."""
        self.client.force_login(user=self.user)
        response = self.client.post(
            self.path_name, {"report_id": self.nonexistent_report_id}
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "audit/resubmission_start_form.html")
        self.assertIn("form", response.context)
        self.assertIn("not found", str(response.context["form"].errors))

    def test_valid_report_id(self):
        """Test that a valid report_id for an exisiting audit redirects to submission start."""
        self.client.force_login(user=self.user)
        response = self.client.post(self.path_name, {"report_id": self.valid_report_id})

        self.assertRedirects(response, reverse("report_submission:eligibility"))
