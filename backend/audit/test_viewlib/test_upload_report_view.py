from unittest.mock import patch

from audit.models import (
    Access,
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
