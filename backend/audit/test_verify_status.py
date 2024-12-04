from .models import (
    Access,
    SingleAuditChecklist,
    User,
)
from audit.models.models import STATUS
from audit.views.views import verify_status

from django.test import TestCase
from django.urls import reverse

from model_bakery import baker
from unittest.mock import Mock


class TestVerifyStatus(TestCase):
    def _test_verify_status(self, sac_status, required_status):
        """
        Helper to test the behavior of a method decorated with verify_status
        sac_status - Current status of the sac
        required_status - The required status to be provided to the decorator
        """
        # Set up the sac and user
        sac = baker.make(SingleAuditChecklist, submission_status=sac_status)
        user = baker.make(User)
        baker.make(Access, user=user, sac=sac, role="editor")
        self.client.force_login(user)

        # Set up a fake method to decorate
        decorator = verify_status(required_status)
        func = Mock()
        mock_view = Mock()
        mock_request = Mock()
        decorated_func = decorator(func)

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

    def test_valid(self):
        """
        Case where the current and required statuses match
        """
        self._test_verify_status(
            sac_status=STATUS.IN_PROGRESS,
            required_status=STATUS.IN_PROGRESS,
        )

    def test_invalid(self):
        """
        Case where the current and required statuses differ
        """
        self._test_verify_status(
            sac_status=STATUS.IN_PROGRESS,
            required_status=STATUS.AUDITEE_CERTIFIED,
        )
