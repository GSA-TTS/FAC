from audit.models import (
    SingleAuditChecklist,
)
from audit.models.constants import STATUS
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from model_bakery import baker

User = get_user_model()


class RemoveSubmissionViewTests(TestCase):
    def setUp(self):
        """Setup client, user, valid/invalid statuses, and a report for each status"""
        self.client = Client()
        self.user = baker.make(User)
        self.client.force_login(self.user)

        # Static info
        self.template = "audit/remove-submission-in-progress.html"
        self.general_information = {
            "auditee_uei": "auditee_uei",
            "auditee_name": "auditee_name",
            "fiscal_year_end_date": "01/01/2022",
            "auditee_fiscal_period_end": "01/01/2022",
        }

        # Valid/invalid statuses. Create one report per status. Create one access per report.
        self.valid_removal_statuses = [
            STATUS.IN_PROGRESS,
            STATUS.READY_FOR_CERTIFICATION,
            STATUS.AUDITOR_CERTIFIED,
            STATUS.AUDITEE_CERTIFIED,
            STATUS.CERTIFIED,
        ]
        self.invalid_removal_statuses = [
            STATUS.SUBMITTED,
            STATUS.DISSEMINATED,
            STATUS.FLAGGED_FOR_REMOVAL,
        ]
        self.reports = [
            baker.make(
                SingleAuditChecklist,
                report_id=f"test-report-id--{status}",
                submission_status=status,
                general_information=self.general_information,
            )
            for status in self.valid_removal_statuses + self.invalid_removal_statuses
        ]
        for report in self.reports:
            baker.make(
                "audit.Access",
                email=self.user.email,
                sac=report,
                user=self.user,
                role="certifying_auditor_contact",
            )

    def test_get_view_permission_denied(self):
        url = reverse(
            "audit:RemoveSubmissionInProgress", kwargs={"report_id": "non-existent-id"}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_post_view_permission_denied(self):
        """Test that POST returns 403 if SAC report_id does not exist"""
        url = reverse(
            "audit:RemoveSubmissionInProgress", kwargs={"report_id": "non-existent-id"}
        )
        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)

    def test_get_view_renders_correct_template(self):
        """
        Test that GET correctly filters out reports of invalid status.
        """
        # For all possible report statuses, get the associated report and report_id. Make a GET request to the removal URL.
        for status in self.valid_removal_statuses + self.invalid_removal_statuses:
            report = next(
                (x for x in self.reports if x.submission_status == status), None
            )
            report_id = report.report_id
            url_removal = reverse(
                "audit:RemoveSubmissionInProgress", kwargs={"report_id": report_id}
            )
            response = self.client.get(url_removal, follow=True)
            url_after = response.request.get("PATH_INFO")

            # If the GET request was made with valid report status, expect the correct template to load.
            # Otherwise, expect to be redirected to the submission checklist.
            if status in self.valid_removal_statuses:
                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, self.template)
            elif status == STATUS.FLAGGED_FOR_REMOVAL:
                # Special case. The user cannot access a flagged record.
                self.assertEqual(response.status_code, 403)
            else:
                url_checklist = reverse(
                    "audit:SubmissionProgress", kwargs={"report_id": report_id}
                )
                self.assertEqual(url_after, url_checklist)

    def test_post_view_flags_correct_reports(self):
        """
        Test that POST correctly filters out reports of invalid status, and flags reports of valid status for removal.
        """
        url_audit_submissions = reverse("audit:MySubmissions")

        # For all possible report statuses, get the associated report and report_id. Make a POST request to the removal URL.
        for status in self.valid_removal_statuses + self.invalid_removal_statuses:
            report = next(
                (x for x in self.reports if x.submission_status == status), None
            )
            report_id = report.report_id
            url_removal = reverse(
                "audit:RemoveSubmissionInProgress", kwargs={"report_id": report_id}
            )
            response = self.client.post(url_removal, follow=True)
            report_after = SingleAuditChecklist.objects.get(report_id=report_id)
            url_after = response.request.get("PATH_INFO")

            # If the POST request was made with valid report status, expect the audit submisisons page to load. Verify that the report has been flagged.
            # Otherwise, expect to be redirected to the submission checklist. Verify the report was not flagged.
            if status in self.valid_removal_statuses:
                self.assertEqual(url_after, url_audit_submissions)
                self.assertEqual(
                    report_after.submission_status, STATUS.FLAGGED_FOR_REMOVAL
                )
            elif status == STATUS.FLAGGED_FOR_REMOVAL:
                # Special case. The user cannot access a flagged record.
                self.assertEqual(response.status_code, 403)
                self.assertEqual(report_after.submission_status, status)
            else:
                url_checklist = reverse(
                    "audit:SubmissionProgress", kwargs={"report_id": report_id}
                )
                self.assertEqual(url_after, url_checklist)
                self.assertEqual(report_after.submission_status, status)
