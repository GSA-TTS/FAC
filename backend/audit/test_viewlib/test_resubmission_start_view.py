from model_bakery import baker

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from audit.models import SingleAuditChecklist
from audit.models.constants import STATUS
from dissemination.models import General

User = get_user_model()


class ResubmissionStartViewTests(TestCase):
    path_name = reverse("audit:ResubmissionStart")
    invalid_report_id = "NOT-LONG-ENOUGH"
    nonexistent_report_id = "LONGENOUGHBUTDOESNOTEXIST"
    valid_report_id = "0123-01-SOURCE-0123456789"
    valid_sibling_report_id = "3210-10-SOURCE-9876543210"
    valid_material_change_reasons = ["findings"]
    valid_resubmission_action = "audit_pdf"
    valid_non_material_change_reasons = ["spelling"]
    valid_non_material_resubmission_action = "non_material_pdf"
    valid_sfsac_resubmission_action = "sfsac_only"
    valid_resubmission_requester = ["auditee"]
    valid_audit_opinion_changes = (
        "The auditor's opinion changed due to revised findings in the audit report."
    )
    valid_sfsac_resubmission_action = "sfsac_only"

    general_information = {
        "auditee_uei": "auditee_uei",
        "auditee_name": "auditee_name",
        "auditee_fiscal_period_start": "2021-01-01",
        "auditee_fiscal_period_end": "2022-01-01",
    }

    def setUp(self):
        """Setup prerequisite fake submissions, then add a user and client."""
        self.valid_sac = baker.make(
            SingleAuditChecklist,
            report_id=self.valid_report_id,
            submission_status=STATUS.DISSEMINATED,
            general_information=self.general_information,
        )
        self.sibling_sac = baker.make(
            SingleAuditChecklist,
            report_id=self.valid_sibling_report_id,
            submission_status=STATUS.DISSEMINATED,
            general_information=self.general_information,
        )
        self.sibling_general = baker.make(
            General,
            report_id=self.valid_sibling_report_id,
            audit_year="2022",
            auditee_uei="auditee_uei",
        )

        self.user = baker.make(User)
        self.client = Client()

    def test_redirect_if_not_logged_in(self):
        """Test that accessing resubmission start page redirects if the user is not logged in."""
        response = self.client.get(self.path_name)
        self.assertEqual(response.status_code, 302)

    def test_invalid_report_id(self):
        """Test that an invalid report_id reloads the page with an error message."""
        self.client.force_login(user=self.user)
        response = self.client.post(
            self.path_name,
            {
                "report_id": self.invalid_report_id,
                "material_change_reasons": self.valid_material_change_reasons,
                "resubmission_action": self.valid_resubmission_action,
                "resubmission_requester": self.valid_resubmission_requester,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "audit/resubmission_start_form.html")
        self.assertIn("form", response.context)
        self.assertIn("too short", str(response.context["form"].errors))

    def test_nonexistent_report(self):
        """Test that a report_id for an audit that does not exist reloads the page with an error message."""
        self.client.force_login(user=self.user)
        response = self.client.post(
            self.path_name,
            {
                "report_id": self.nonexistent_report_id,
                "material_change_reasons": self.valid_material_change_reasons,
                "resubmission_action": self.valid_resubmission_action,
                "resubmission_requester": self.valid_resubmission_requester,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "audit/resubmission_start_form.html")
        self.assertIn("form", response.context)
        self.assertIn("not found", str(response.context["form"].errors))

    def test_valid_report_id(self):
        """Test that a valid report_id for an existing audit redirects to submission start."""
        self.client.force_login(user=self.user)
        response = self.client.post(
            self.path_name,
            {
                "report_id": self.valid_report_id,
                "material_change_reasons": self.valid_material_change_reasons,
                "resubmission_action": self.valid_resubmission_action,
                "resubmission_requester": self.valid_resubmission_requester,
                "audit_opinion_changes": self.valid_audit_opinion_changes,
            },
        )

        self.assertRedirects(
            response,
            reverse("report_submission:eligibility"),
            fetch_redirect_response=False,
        )

    def test_material_change_reasons_required(self):
        """Test that at least one material change reason must be selected."""
        self.client.force_login(user=self.user)
        response = self.client.post(
            self.path_name,
            {
                "report_id": self.valid_report_id,
                "resubmission_action": self.valid_resubmission_action,
                "resubmission_requester": self.valid_resubmission_requester,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "audit/resubmission_start_form.html")
        self.assertIn("form", response.context)
        self.assertIn(
            "Select at least one material change.",
            str(response.context["form"].errors),
        )

    def test_resubmission_action_required(self):
        """Test that a resubmission action must be selected."""
        self.client.force_login(user=self.user)
        response = self.client.post(
            self.path_name,
            {
                "report_id": self.valid_report_id,
                "material_change_reasons": self.valid_material_change_reasons,
                "resubmission_requester": self.valid_resubmission_requester,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "audit/resubmission_start_form.html")
        self.assertIn("form", response.context)
        self.assertIn(
            "Select the type of change you need to make.",
            str(response.context["form"].errors),
        )

    def test_resubmission_action_saved_to_profile(self):
        """Test that the selected resubmission action is saved to the user profile."""
        self.client.force_login(user=self.user)
        response = self.client.post(
            self.path_name,
            {
                "report_id": self.valid_report_id,
                "resubmission_action": self.valid_sfsac_resubmission_action,
                "resubmission_requester": self.valid_resubmission_requester,
            },
        )

        self.assertRedirects(
            response,
            reverse("report_submission:eligibility"),
            fetch_redirect_response=False,
        )

        self.user.profile.refresh_from_db()
        self.assertEqual(
            self.user.profile.entry_form_data["resubmission_meta"][
                "resubmission_action"
            ],
            self.valid_sfsac_resubmission_action,
        )

    def test_non_material_change_reasons_required(self):
        """Test that at least one non-material change reason must be selected."""
        self.client.force_login(user=self.user)
        response = self.client.post(
            self.path_name,
            {
                "report_id": self.valid_report_id,
                "resubmission_action": self.valid_non_material_resubmission_action,
                "resubmission_requester": self.valid_resubmission_requester,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "audit/resubmission_start_form.html")
        self.assertIn("form", response.context)
        self.assertIn(
            "Select at least one non-material change.",
            str(response.context["form"].errors),
        )

    def test_valid_non_material_pdf_resubmission(self):
        self.client.force_login(user=self.user)

        response = self.client.post(
            self.path_name,
            {
                "report_id": self.valid_report_id,
                "non_material_change_reasons": self.valid_non_material_change_reasons,
                "resubmission_action": self.valid_non_material_resubmission_action,
                "resubmission_requester": self.valid_resubmission_requester,
            },
        )

        self.assertRedirects(
            response,
            reverse("report_submission:eligibility"),
            fetch_redirect_response=False,
        )

    def test_audit_opinion_changes_saved_for_audit_pdf_resubmission(self):
        """Test that audit opinion changes are saved for a full audit PDF resubmission."""
        self.client.force_login(user=self.user)

        response = self.client.post(
            self.path_name,
            {
                "report_id": self.valid_report_id,
                "material_change_reasons": self.valid_material_change_reasons,
                "resubmission_action": self.valid_resubmission_action,
                "resubmission_requester": self.valid_resubmission_requester,
                "audit_opinion_changes": self.valid_audit_opinion_changes,
            },
        )

        self.assertRedirects(
            response,
            reverse("report_submission:eligibility"),
            fetch_redirect_response=False,
        )

        self.user.profile.refresh_from_db()

        self.assertEqual(
            self.user.profile.entry_form_data["resubmission_meta"][
                "audit_opinion_changes"
            ],
            self.valid_audit_opinion_changes,
        )

    def test_longform_audit_opinion_changes_saved(self):
        """Test that long-form audit opinion changes are saved without truncation."""
        self.client.force_login(user=self.user)

        audit_opinion_changes = (
            "The auditor's opinion was revised after additional documentation "
            "was reviewed. The updated audit report includes changes to the "
            "findings, compliance determination, and supporting explanation.\n\n"
            "Additional details regarding the revised opinion are included "
            "in the resubmitted audit package."
        )

        response = self.client.post(
            self.path_name,
            {
                "report_id": self.valid_report_id,
                "material_change_reasons": self.valid_material_change_reasons,
                "resubmission_action": self.valid_resubmission_action,
                "resubmission_requester": self.valid_resubmission_requester,
                "audit_opinion_changes": audit_opinion_changes,
            },
        )

        self.assertRedirects(
            response,
            reverse("report_submission:eligibility"),
            fetch_redirect_response=False,
        )

        self.user.profile.refresh_from_db()

        self.assertEqual(
            self.user.profile.entry_form_data["resubmission_meta"][
                "audit_opinion_changes"
            ],
            audit_opinion_changes,
        )

    def test_audit_opinion_changes_cleared_for_sfsac_only_resubmission(self):
        """Test that audit opinion changes are not saved for an SF-SAC-only resubmission."""
        self.client.force_login(user=self.user)

        response = self.client.post(
            self.path_name,
            {
                "report_id": self.valid_report_id,
                "resubmission_action": self.valid_sfsac_resubmission_action,
                "resubmission_requester": self.valid_resubmission_requester,
                "audit_opinion_changes": self.valid_audit_opinion_changes,
            },
        )

        self.assertRedirects(
            response,
            reverse("report_submission:eligibility"),
            fetch_redirect_response=False,
        )

        self.user.profile.refresh_from_db()

        self.assertEqual(
            self.user.profile.entry_form_data["resubmission_meta"][
                "audit_opinion_changes"
            ],
            "",
        )

    def test_audit_opinion_changes_cleared_for_non_material_pdf_resubmission(self):
        self.client.force_login(user=self.user)

        response = self.client.post(
            self.path_name,
            {
                "report_id": self.valid_report_id,
                "non_material_change_reasons": self.valid_non_material_change_reasons,
                "resubmission_action": self.valid_non_material_resubmission_action,
                "resubmission_requester": self.valid_resubmission_requester,
                "audit_opinion_changes": self.valid_audit_opinion_changes,
            },
        )

        self.assertRedirects(
            response,
            reverse("report_submission:eligibility"),
            fetch_redirect_response=False,
        )

        self.user.profile.refresh_from_db()

        self.assertEqual(
            self.user.profile.entry_form_data["resubmission_meta"][
                "audit_opinion_changes"
            ],
            "",
        )

    def test_audit_opinion_changes_required_for_audit_pdf_resubmission(self):
        self.client.force_login(user=self.user)

        response = self.client.post(
            self.path_name,
            {
                "report_id": self.valid_report_id,
                "material_change_reasons": self.valid_material_change_reasons,
                "resubmission_action": self.valid_resubmission_action,
                "resubmission_requester": self.valid_resubmission_requester,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Identify the changes in the audit opinion that are the reason for the resubmission.",
            str(response.context["form"].errors),
        )
