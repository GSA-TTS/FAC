from django.test import TestCase
from audit.models import SingleAuditChecklist
from .check_resubmission_has_changes import (
    check_resubmission_has_changes,
)
from .sac_validation_shape import sac_validation_shape
from .errors import err_identical_resubmissions

from model_bakery import baker
from unittest.mock import patch


class CheckResubmissionHasChangesTest(TestCase):
    def _make_resub(self, version, previous_report_id) -> SingleAuditChecklist:
        sac = baker.make(SingleAuditChecklist, report_id="resub")
        sac.resubmission_meta = {
            "version": version,
            "previous_report_id": previous_report_id,
        }
        sac.save()

        return sac

    # Patching compare_single_audit_reports because it hits S3
    @patch("audit.viewlib.compare_two_submissions.compare_single_audit_reports")
    def test_has_no_changes(self, mock_sar_compare):
        """When there are no changes, we should have an error"""
        orig = baker.make(SingleAuditChecklist)
        resub = self._make_resub(2, orig.report_id)
        shaped_resub = sac_validation_shape(resub)
        mock_sar_compare.return_value = {"status": "same"}

        errors = check_resubmission_has_changes(shaped_resub)

        self.assertEqual(
            errors, [{"error": err_identical_resubmissions(orig.report_id)}]
        )

    @patch("audit.viewlib.compare_two_submissions.compare_single_audit_reports")
    def test_has_changes(self, mock_sar_compare):
        """When there are changes, we should not have an error"""
        orig = baker.make(SingleAuditChecklist)
        resub = self._make_resub(2, orig.report_id)
        shaped_resub = sac_validation_shape(resub)
        mock_sar_compare.return_value = {"status": "changed"}

        errors = check_resubmission_has_changes(shaped_resub)

        self.assertEqual(errors, [])
