from unittest.mock import patch

from audit.models import (
    Access,
    SingleAuditReportFile,
    SubmissionEvent,
)
from audit.models.constants import SAC_SEQUENCE_ID
from audit.models.utils import get_next_sequence_id
from audit.test_views import (
    _mock_gen_report_id,
    _mock_login_and_scan,
    _make_user_and_sac,
)
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker

User = get_user_model()


class SingleAuditReportFileHandlerViewTests(TestCase):
    valid_page_numbers = {
        "financial_statements": 1,
        "financial_statements_opinion": 2,
        "schedule_expenditures": 3,
        "schedule_expenditures_opinion": 4,
        "uniform_guidance_control": 5,
        "uniform_guidance_compliance": 6,
        "GAS_control": 7,
        "GAS_compliance": 8,
        "schedule_findings": 9,
    }

    def test_login_required(self):
        """When an unauthenticated request is made."""

        response = self.client.post(
            reverse(
                "audit:SingleAuditReport",
                kwargs={"report_id": "12345"},
            )
        )

        self.assertTemplateUsed(response, "home.html")
        self.assertTrue(response.context["session_expired"])

    def test_bad_report_id_returns_403(self):
        """When a request is made for a malformed or nonexistent report_id, a 403 error should be returned."""
        user = baker.make(User)

        self.client.force_login(user)

        response = self.client.post(
            reverse(
                "audit:SingleAuditReport",
                kwargs={
                    "report_id": "this is not a report id",
                },
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_inaccessible_audit_returns_403(self):
        """When a request is made for an audit that is inaccessible for this user, a 403 error should be returned."""
        user, sac = _make_user_and_sac()

        self.client.force_login(user)
        response = self.client.post(
            reverse(
                "audit:SingleAuditReport",
                kwargs={"report_id": sac.report_id},
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_no_file_attached_returns_400(self):
        """When a request is made with no file attached, a 400 error should be returned."""
        user, sac = _make_user_and_sac()
        baker.make(Access, user=user, sac=sac)

        self.client.force_login(user)

        response = self.client.post(
            reverse(
                "audit:SingleAuditReport",
                kwargs={"report_id": sac.report_id},
            )
        )

        self.assertEqual(response.status_code, 400)

    @patch("audit.validators._scan_file")
    def test_valid_file_upload(self, mock_scan_file):
        """Test that uploading a valid SAR update the SAC accordingly."""
        sequence = get_next_sequence_id(SAC_SEQUENCE_ID)
        sac = _mock_login_and_scan(
            self.client,
            mock_scan_file,
            id=sequence,
            report_id=_mock_gen_report_id(sequence),
        )

        with open("audit/fixtures/basic.pdf", "rb") as pdf_file:
            response = self.client.post(
                reverse(
                    "audit:SingleAuditReport",
                    kwargs={
                        "report_id": sac.report_id,
                    },
                ),
                data={"FILES": pdf_file},
            )

            self.assertEqual(response.status_code, 302)

        submission_events = SubmissionEvent.objects.filter(sac=sac)

        # the most recent event should be AUDIT_REPORT_PDF_UPDATED
        event_count = len(submission_events)
        self.assertGreaterEqual(event_count, 1)
        self.assertEqual(
            submission_events[event_count - 1].event,
            SubmissionEvent.EventType.AUDIT_REPORT_PDF_UPDATED,
        )

    @patch("audit.validators._scan_file")
    def test_new_report_upload_via_upload_report_view(self, mock_scan_file):
        """
        When a user uploads a new report, `keep_previous_report` is either False or absent.
        Ensure the view redirects the user. Then pull down the SAR and spot check the data and file.
        """
        sequence = get_next_sequence_id(SAC_SEQUENCE_ID)
        sac = _mock_login_and_scan(
            self.client,
            mock_scan_file,
            id=sequence,
            report_id=_mock_gen_report_id(sequence),
        )

        with open("audit/fixtures/basic.pdf", "rb") as pdf_file:
            response = self.client.post(
                reverse(
                    "audit:UploadReport",
                    kwargs={"report_id": sac.report_id},
                ),
                data={**self.valid_page_numbers, "upload_report": pdf_file},
            )

        self.assertEqual(response.status_code, 302)

        sar = SingleAuditReportFile.objects.filter(sac=sac).latest("date_created")
        self.assertIsNotNone(sar)
        self.assertEqual(
            sar.component_page_numbers["schedule_findings"],
            self.valid_page_numbers["schedule_findings"],
        )

    @patch("audit.views.upload_report_view.copy_file")
    @patch("audit.validators._scan_file")
    def test_keep_previous_report_copies_data(self, mock_scan_file, mock_copy_file):
        """
        When a user opts to copy their report during a resubmission, `keep_previous_report` is either True.
        Create a previous report. Ensure the view redirects the user. Ensure `copy_file` was run with the right params. Spot check the data and file.
        """
        # Create the necessary "previous" report data.
        prev_sequence = get_next_sequence_id(SAC_SEQUENCE_ID)
        prev_sac = _mock_login_and_scan(
            self.client,
            mock_scan_file,
            id=prev_sequence,
            report_id=_mock_gen_report_id(prev_sequence),
        )

        baker.make(
            SingleAuditReportFile,
            sac=prev_sac,
            file=f"singleauditreport/{prev_sac.report_id}.pdf",
            filename=f"{prev_sac.report_id}.pdf",
            component_page_numbers=self.valid_page_numbers,
        )

        # Create the necessary "current" report data, link it to the "previous".
        current_sequence = get_next_sequence_id(SAC_SEQUENCE_ID)
        current_sac = _mock_login_and_scan(
            self.client,
            mock_scan_file,
            id=current_sequence,
            report_id=_mock_gen_report_id(current_sequence),
            resubmission_meta={"previous_report_id": prev_sac.report_id},
        )

        # POST with keep_previous_report checked
        response = self.client.post(
            reverse(
                "audit:UploadReport",
                kwargs={"report_id": current_sac.report_id},
            ),
            data={"keep_previous_report": True},
        )

        self.assertEqual(response.status_code, 302)

        # Ensure the copy function was called.
        mock_copy_file.assert_called_once_with(
            f"singleauditreport/{prev_sac.report_id}.pdf",
            f"singleauditreport/{current_sac.report_id}.pdf",
        )

        # Spot check the "new" file.
        new_sar = SingleAuditReportFile.objects.filter(sac=current_sac).latest(
            "date_created"
        )
        self.assertIsNotNone(new_sar)
        self.assertEqual(
            new_sar.component_page_numbers["schedule_findings"],
            self.valid_page_numbers["schedule_findings"],
        )
