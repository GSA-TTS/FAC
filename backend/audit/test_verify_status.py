from .decorators import verify_status
from .models import (
    Access,
    SingleAuditChecklist,
    User,
)
from audit.models.models import STATUS


from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse

from model_bakery import baker
from unittest.mock import Mock


class TestVerifyStatus(TestCase):
    def _test_verify_status(self, sac_status, required_status, sac_exists):
        """
        Helper to test the behavior of a method decorated with verify_status
        sac_status - Current status of the sac
        required_status - The required status to be provided to the decorator
        """
        user = baker.make(User)
        self.client.force_login(user)

        if sac_exists:
            sac = baker.make(SingleAuditChecklist, submission_status=sac_status)
            baker.make(Access, user=user, sac=sac, role="editor")

        # Set up a fake method to decorate
        decorator = verify_status(required_status)
        func = Mock()
        mock_view = Mock()
        mock_request = Mock()
        decorated_func = decorator(func)

        if sac_exists:
            result = decorated_func(mock_view, mock_request, report_id=sac.report_id)

            if sac_status == required_status:
                # The decorated method should be called as normal if the statuses match
                func.assert_called()
            else:
                # The decorated method should redirect if the statuses don't match
                result.client = self.client
                self.assertRedirects(
                    result,
                    reverse("audit:SubmissionProgress", args=[sac.report_id]),
                )
        else:
            with self.assertRaises(PermissionDenied):
                decorated_func(mock_view, mock_request, report_id="bad_report_id")

    def test_valid(self):
        """
        Current and required statuses matching should pass
        """
        self._test_verify_status(
            sac_status=STATUS.IN_PROGRESS,
            required_status=STATUS.IN_PROGRESS,
            sac_exists=True,
        )

    def test_invalid(self):
        """
        Current and required statuses differing should pass
        """
        self._test_verify_status(
            sac_status=STATUS.IN_PROGRESS,
            required_status=STATUS.AUDITEE_CERTIFIED,
            sac_exists=True,
        )

    def test_no_sac(self):
        """
        Current and required statuses differing should throw
        """
        self._test_verify_status(
            sac_status=STATUS.IN_PROGRESS,
            required_status=STATUS.AUDITEE_CERTIFIED,
            sac_exists=False,
        )
