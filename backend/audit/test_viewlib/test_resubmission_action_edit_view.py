from model_bakery import baker

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from audit.models import Access, SingleAuditChecklist
from audit.models.constants import RESUBMISSION_ACTION, STATUS

User = get_user_model()


class ResubmissionActionEditViewTests(TestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.client = Client()
        self.client.force_login(self.user)

        self.sac = baker.make(
            SingleAuditChecklist,
            submission_status=STATUS.IN_PROGRESS,
            resubmission_meta={
                "resubmission_action": RESUBMISSION_ACTION.NON_MATERIAL_PDF,
                "resubmission_requester": ["auditee"],
                "material_change_reasons": [],
                "non_material_change_reasons": ["spelling"],
                "audit_opinion_changes": "Existing non-material PDF edits.",
            },
        )

        baker.make(
            Access,
            sac=self.sac,
            user=self.user,
        )

        self.path = reverse(
            "audit:ResubmissionActionEdit",
            kwargs={"report_id": self.sac.report_id},
        )

    def test_get_populates_existing_non_material_pdf_values(self):
        response = self.client.get(self.path)

        self.assertEqual(response.status_code, 200)

        form = response.context["form"]

        self.assertEqual(
            form.initial["resubmission_action"],
            RESUBMISSION_ACTION.NON_MATERIAL_PDF,
        )
        self.assertEqual(
            form.initial["resubmission_requester"],
            ["auditee"],
        )
        self.assertEqual(
            form.initial["non_material_change_reasons"],
            ["spelling"],
        )
        self.assertEqual(
            form.initial["audit_opinion_changes"],
            "Existing non-material PDF edits.",
        )

    def test_non_material_pdf_optional_text_is_saved(self):
        response = self.client.post(
            self.path,
            {
                "resubmission_action": RESUBMISSION_ACTION.NON_MATERIAL_PDF,
                "resubmission_requester": ["auditee"],
                "material_change_reasons": [],
                "non_material_change_reasons": ["spelling"],
                "audit_opinion_changes": "Updated non-material PDF edits.",
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "audit:SubmissionProgress",
                kwargs={"report_id": self.sac.report_id},
            ),
            fetch_redirect_response=False,
        )

        self.sac.refresh_from_db()

        self.assertEqual(
            self.sac.resubmission_meta["audit_opinion_changes"],
            "Updated non-material PDF edits.",
        )

    def test_non_material_pdf_text_is_optional(self):
        response = self.client.post(
            self.path,
            {
                "resubmission_action": RESUBMISSION_ACTION.NON_MATERIAL_PDF,
                "resubmission_requester": ["auditee"],
                "material_change_reasons": [],
                "non_material_change_reasons": ["spelling"],
                "audit_opinion_changes": "",
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "audit:SubmissionProgress",
                kwargs={"report_id": self.sac.report_id},
            ),
            fetch_redirect_response=False,
        )

    def test_material_pdf_requires_audit_opinion_changes(self):
        response = self.client.post(
            self.path,
            {
                "resubmission_action": RESUBMISSION_ACTION.AUDIT_PDF,
                "resubmission_requester": ["auditee"],
                "material_change_reasons": ["findings"],
                "non_material_change_reasons": [],
                "audit_opinion_changes": "",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Identify the changes in the audit opinion that are the reason for the resubmission.",
            str(response.context["form"].errors),
        )

    def test_sfsac_only_clears_audit_opinion_changes(self):
        response = self.client.post(
            self.path,
            {
                "resubmission_action": RESUBMISSION_ACTION.SFSAC_ONLY,
                "resubmission_requester": ["auditee"],
                "material_change_reasons": [],
                "non_material_change_reasons": [],
                "audit_opinion_changes": "This should be removed.",
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "audit:SubmissionProgress",
                kwargs={"report_id": self.sac.report_id},
            ),
            fetch_redirect_response=False,
        )

        self.sac.refresh_from_db()

        self.assertEqual(
            self.sac.resubmission_meta["audit_opinion_changes"],
            "",
        )

    def test_resubmission_action_can_be_changed(self):
        response = self.client.post(
            self.path,
            {
                "resubmission_action": RESUBMISSION_ACTION.SFSAC_ONLY,
                "resubmission_requester": ["auditee"],
                "material_change_reasons": [],
                "non_material_change_reasons": [],
                "audit_opinion_changes": "",
            },
        )

        self.assertRedirects(
            response,
            reverse(
                "audit:SubmissionProgress",
                kwargs={"report_id": self.sac.report_id},
            ),
            fetch_redirect_response=False,
        )

        self.sac.refresh_from_db()

        self.assertEqual(
            self.sac.resubmission_meta["resubmission_action"],
            RESUBMISSION_ACTION.SFSAC_ONLY,
        )
