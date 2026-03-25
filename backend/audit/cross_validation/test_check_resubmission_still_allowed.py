from unittest.mock import patch

from audit.models import SingleAuditChecklist
from django.test import TestCase

from audit.cross_validation.check_resubmission_still_allowed import (
    check_resubmission_still_allowed,
)


class CheckResubmissionStillAllowedTests(TestCase):
    def test_returns_error_when_report_id_is_missing(self):
        sac_data = {
            "sf_sac_meta": {},
            "sf_sac_sections": {},
        }

        result = check_resubmission_still_allowed(sac_data)

        self.assertEqual(result, [])

    @patch("audit.models.SingleAuditChecklist.objects.get")
    def test_returns_error_when_sac_cannot_be_found(self, mock_get):
        mock_get.side_effect = SingleAuditChecklist.DoesNotExist

        sac_data = {
            "sf_sac_meta": {"report_id": "R1"},
            "sf_sac_sections": {},
        }

        result = check_resubmission_still_allowed(sac_data)

        self.assertEqual(result, [])

    @patch(
        "audit.cross_validation.check_resubmission_still_allowed.check_resubmission_allowed"
    )
    @patch("audit.models.SingleAuditChecklist.objects.get")
    def test_returns_friendly_error_when_resubmission_is_not_allowed(
        self, mock_get, mock_check_allowed
    ):
        class MockSAC:
            resubmission_meta = {"version": 1}

        mock_sac = MockSAC()
        mock_get.return_value = mock_sac
        mock_check_allowed.return_value = (False, "not allowed")

        sac_data = {
            "sf_sac_meta": {"report_id": "R3"},
            "sf_sac_sections": {},
        }

        result = check_resubmission_still_allowed(sac_data)

        self.assertEqual(
            result,
            [
                {
                    "error": (
                        "This audit is no longer eligible for resubmission. Another "
                        "resubmission may already have been submitted. Please refresh "
                        "and start from the most recent version."
                    )
                }
            ],
        )

    @patch(
        "audit.cross_validation.check_resubmission_still_allowed.check_resubmission_allowed"
    )
    @patch("audit.models.SingleAuditChecklist.objects.get")
    def test_returns_empty_list_when_resubmission_is_allowed(
        self, mock_get, mock_check_allowed
    ):
        class MockSAC:
            resubmission_meta = {"version": 1}

        mock_sac = MockSAC()
        mock_get.return_value = mock_sac
        mock_check_allowed.return_value = (True, "allowed")

        sac_data = {
            "sf_sac_meta": {"report_id": "R4"},
            "sf_sac_sections": {},
        }

        result = check_resubmission_still_allowed(sac_data)

        self.assertEqual(result, [])
