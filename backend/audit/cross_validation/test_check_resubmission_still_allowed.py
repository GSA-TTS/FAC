from unittest.mock import patch

from audit.models import SingleAuditChecklist
from django.test import TestCase

from audit.cross_validation.check_resubmission_still_allowed import (
    check_resubmission_still_allowed,
)


class CheckResubmissionStillAllowedTests(TestCase):
    def test_returns_empty_list_when_resubmission_meta_is_missing(self):
        sac_data = {
            "sf_sac_meta": {},
            "sf_sac_sections": {},
        }

        result = check_resubmission_still_allowed(sac_data)

        self.assertEqual(result, [])

    def test_returns_empty_list_when_previous_report_id_is_missing(self):
        sac_data = {
            "sf_sac_meta": {
                "resubmission_meta": {
                    "version": 2,
                    "resubmission_status": "most_recent",
                }
            },
            "sf_sac_sections": {},
        }

        result = check_resubmission_still_allowed(sac_data)

        self.assertEqual(result, [])

    @patch("audit.models.SingleAuditChecklist.objects.get")
    def test_returns_empty_list_when_parent_sac_cannot_be_found(self, mock_get):
        mock_get.side_effect = SingleAuditChecklist.DoesNotExist

        sac_data = {
            "sf_sac_meta": {
                "resubmission_meta": {
                    "version": 2,
                    "previous_report_id": "P1",
                    "resubmission_status": "most_recent",
                }
            },
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
        class MockParentSAC:
            report_id = "P1"
            resubmission_meta = {
                "version": 1,
                "resubmission_status": "deprecated_via_resubmission",
            }

        mock_get.return_value = MockParentSAC()
        mock_check_allowed.return_value = (
            False,
            "This audit has been deprecated and cannot be resubmitted.",
        )

        sac_data = {
            "sf_sac_meta": {
                "resubmission_meta": {
                    "version": 2,
                    "previous_report_id": "P1",
                    "resubmission_status": "most_recent",
                }
            },
            "sf_sac_sections": {},
        }

        result = check_resubmission_still_allowed(sac_data)

        self.assertEqual(
            result,
            [
                {
                    "error": "This audit has been deprecated and cannot be resubmitted.",
                }
            ],
        )
        mock_get.assert_called_once_with(report_id="P1")

    @patch(
        "audit.cross_validation.check_resubmission_still_allowed.check_resubmission_allowed"
    )
    @patch("audit.models.SingleAuditChecklist.objects.get")
    def test_returns_empty_list_when_resubmission_is_allowed(
        self, mock_get, mock_check_allowed
    ):
        class MockParentSAC:
            report_id = "P2"
            resubmission_meta = {
                "version": 1,
                "resubmission_status": "most_recent",
            }

        mock_get.return_value = MockParentSAC()
        mock_check_allowed.return_value = (True, "allowed")

        sac_data = {
            "sf_sac_meta": {
                "resubmission_meta": {
                    "version": 2,
                    "previous_report_id": "P2",
                    "resubmission_status": "most_recent",
                }
            },
            "sf_sac_sections": {},
        }

        result = check_resubmission_still_allowed(sac_data)

        self.assertEqual(result, [])
        mock_get.assert_called_once_with(report_id="P2")
