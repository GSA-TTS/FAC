from copy import deepcopy
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from model_bakery import baker

from audit.models import SingleAuditChecklist
from audit.models.constants import STATUS

SAC = {
    "report_id": "2022-42-MAGIC-0000000001",
    "submission_status": STATUS.DISSEMINATED,
    "transition_name": [
        "ready_for_certification",
        "auditor_certified",
        "auditee_certified",
        "certified",
        "submitted",
        "disseminated",
    ],
    "transition_date": [
        "2023-09-26T00:00:00.000Z",
        "2023-09-26T10:11:52.000Z",
        "2023-09-26T13:19:56.000Z",
        "2023-09-26T00:00:00.000Z",
        "2023-09-26T00:00:00.000Z",
        "2024-01-20T01:12:35.065Z",
    ],
    "general_information": {
        "ein": "237399677",
        "auditee_uei": "GNU9RNVE6J68",
        "auditee_zip": "15942",
        "auditor_ein": "251390233",
        "auditee_city": "MINERAL POINT",
        "auditee_name": "JACKSON TOWNSHIP VOLUNTEER FIRE COMPANY",
        "auditee_email": "MS74CCHS@ATLANTICBB.NET",
        "auditee_state": "PA",
        "auditee_fiscal_period_end": "2022-12-31",
    },
}


class SuppressAuditCommandTests(TestCase):
    def setUp(self):
        self.user = baker.make(
            User,
            email="admin@example.com",
            is_staff=True,
        )

    def _make_sac(self, status=STATUS.DISSEMINATED):
        return baker.make(
            SingleAuditChecklist,
            **{
                **deepcopy(SAC),
                "submission_status": status,
            },
        )

    def test_command_suppresses_audit(self):
        sac = self._make_sac()
        stdout = StringIO()

        call_command(
            "suppress_audit",
            sac.report_id,
            email=self.user.email,
            stdout=stdout,
        )

        sac.refresh_from_db()

        self.assertEqual(
            sac.submission_status,
            STATUS.FLAGGED_FOR_REMOVAL,
        )

        self.assertIn(
            f"Successfully suppressed audit {sac.report_id}.",
            stdout.getvalue(),
        )

    def test_command_rejects_invalid_report_id(self):
        with self.assertRaisesRegex(
            CommandError,
            "No SAC found",
        ):
            call_command(
                "suppress_audit",
                "missing-report-id",
                email=self.user.email,
            )

    def test_command_rejects_non_staff_user(self):
        user = baker.make(
            User,
            email="not-staff@example.com",
            is_staff=False,
        )

        sac = self._make_sac()

        with self.assertRaisesRegex(
            CommandError,
            "No FAC staff user found",
        ):
            call_command(
                "suppress_audit",
                sac.report_id,
                email=user.email,
            )
