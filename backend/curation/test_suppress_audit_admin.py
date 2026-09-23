from copy import deepcopy
from unittest.mock import patch

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory, TestCase
from model_bakery import baker

from audit.admin import SACAdmin, suppress_disseminated_reports
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
        "auditee_email": "auditee@example.com",
        "auditee_state": "PA",
        "auditee_fiscal_period_end": "2022-12-31",
    },
}


class SuppressAuditAdminTests(TestCase):
    def setUp(self):
        self.user = baker.make(
            User,
            email="admin@example.com",
            is_staff=True,
        )

        self.factory = RequestFactory()
        self.modeladmin = SACAdmin(
            SingleAuditChecklist,
            admin.site,
        )

    def _make_request(self):
        request = self.factory.post("/admin/audit/singleauditchecklist/")
        request.user = self.user

        request.session = {}
        request._messages = FallbackStorage(request)

        return request

    def _make_sac(self, **overrides):
        data = deepcopy(SAC)
        data.update(overrides)

        return baker.make(
            SingleAuditChecklist,
            **data,
        )

    @patch("audit.admin.suppress_audit")
    def test_admin_action_calls_suppress_audit(self, mock_suppress_audit):
        sac = self._make_sac()
        mock_suppress_audit.return_value = sac

        request = self._make_request()
        queryset = SingleAuditChecklist.objects.filter(pk=sac.pk)

        suppress_disseminated_reports(
            self.modeladmin,
            request,
            queryset,
        )

        mock_suppress_audit.assert_called_once_with(
            report_id=sac.report_id,
            email=self.user.email,
        )

        messages = [str(message) for message in request._messages]

        self.assertIn(
            f"Successfully suppressed report(s) ({sac.report_id}).",
            messages,
        )

    @patch("audit.admin.suppress_audit")
    def test_admin_action_displays_error(self, mock_suppress_audit):
        sac = self._make_sac(
            submission_status=STATUS.IN_PROGRESS,
        )

        mock_suppress_audit.side_effect = ValueError(
            f"{sac.report_id} cannot be suppressed from status "
            f"{STATUS.IN_PROGRESS}."
        )

        request = self._make_request()
        queryset = SingleAuditChecklist.objects.filter(pk=sac.pk)

        suppress_disseminated_reports(
            self.modeladmin,
            request,
            queryset,
        )

        messages = [str(message) for message in request._messages]

        self.assertTrue(
            any("Unable to suppress report(s)" in message for message in messages)
        )

    def test_suppress_action_is_registered(self):
        self.assertIn(
            suppress_disseminated_reports,
            self.modeladmin.actions,
        )
