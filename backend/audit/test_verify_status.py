from django.contrib.auth.models import User

from .decorators import verify_status
from .models import (
    Access,
    Audit,
)


from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.urls import reverse

from model_bakery import baker
from unittest.mock import Mock

from .models.constants import STATUS


class TestVerifyStatus(TestCase):
    def _test_verify_status(self, audit_status, required_status, audit_exists):
        """
        Helper to test the behavior of a method decorated with verify_status
        audit_status - Current status of the audit
        required_status - The required status to be provided to the decorator
        """
        user = baker.make(User)
        self.client.force_login(user)

        # Set up a fake method to decorate
        decorator = verify_status(required_status)
        func = Mock()
        mock_view = Mock()
        mock_request = Mock()
        decorated_func = decorator(func)

        if audit_exists:
            audit = baker.make(Audit, version=0, submission_status=audit_status)
            baker.make(Access, user=user, audit=audit, role="editor")
            result = decorated_func(mock_view, mock_request, report_id=audit.report_id)

            if audit_status == required_status:
                # The decorated method should be called as normal if the statuses match
                func.assert_called()
            else:
                # The decorated method should redirect if the statuses don't match
                result.client = self.client
                self.assertRedirects(
                    result,
                    reverse("audit:SubmissionProgress", args=[audit.report_id]),
                )
        else:
            with self.assertRaises(PermissionDenied):
                decorated_func(mock_view, mock_request, report_id="bad_report_id")

    def test_valid(self):
        """
        Current and required statuses matching should pass
        """
        self._test_verify_status(
            audit_status=STATUS.IN_PROGRESS,
            required_status=STATUS.IN_PROGRESS,
            audit_exists=True,
        )

    def test_invalid(self):
        """
        Current and required statuses differing should pass
        """
        self._test_verify_status(
            audit_status=STATUS.IN_PROGRESS,
            required_status=STATUS.AUDITEE_CERTIFIED,
            audit_exists=True,
        )

    def test_no_sac(self):
        """
        Current and required statuses differing should throw
        """
        self._test_verify_status(
            audit_status=STATUS.IN_PROGRESS,
            required_status=STATUS.AUDITEE_CERTIFIED,
            audit_exists=False,
        )
