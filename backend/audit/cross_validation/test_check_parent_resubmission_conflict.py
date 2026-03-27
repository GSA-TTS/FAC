from unittest.mock import patch

from audit.models import SingleAuditChecklist
from django.test import TestCase

from audit.cross_validation.check_parent_resubmission_conflict import (
    check_parent_resubmission_conflict,
)


class CheckParentResubmissionConflictTests(TestCase):
    def test_returns_empty_list_when_report_id_is_missing(self):
        sac_data = {
            "sf_sac_meta": {},
            "sf_sac_sections": {},
        }

        result = check_parent_resubmission_conflict(sac_data)

        self.assertEqual(result, [])

    @patch("audit.models.SingleAuditChecklist.objects.get")
    def test_returns_empty_list_when_sac_cannot_be_found(self, mock_get):
        mock_get.side_effect = SingleAuditChecklist.DoesNotExist

        sac_data = {
            "sf_sac_meta": {"report_id": "R1"},
            "sf_sac_sections": {},
        }

        result = check_parent_resubmission_conflict(sac_data)

        self.assertEqual(result, [])

    @patch("audit.models.SingleAuditChecklist.objects.exclude")
    @patch("audit.models.SingleAuditChecklist.objects.get")
    def test_returns_empty_list_when_not_a_resubmission(self, mock_get, mock_exclude):
        class MockSAC:
            resubmission_meta = None

        mock_get.return_value = MockSAC()

        sac_data = {
            "sf_sac_meta": {"report_id": "R2"},
            "sf_sac_sections": {},
        }

        result = check_parent_resubmission_conflict(sac_data)

        self.assertEqual(result, [])
        mock_exclude.assert_not_called()

    @patch("audit.models.SingleAuditChecklist.objects.exclude")
    @patch("audit.models.SingleAuditChecklist.objects.get")
    def test_returns_empty_list_when_no_parent_report_id(self, mock_get, mock_exclude):
        class MockSAC:
            resubmission_meta = {"version": 2, "resubmission_status": "most_recent"}

        mock_get.return_value = MockSAC()

        sac_data = {
            "sf_sac_meta": {"report_id": "R3"},
            "sf_sac_sections": {},
        }

        result = check_parent_resubmission_conflict(sac_data)

        self.assertEqual(result, [])
        mock_exclude.assert_not_called()

    @patch("audit.models.SingleAuditChecklist.objects.exclude")
    @patch("audit.models.SingleAuditChecklist.objects.get")
    def test_returns_empty_list_when_no_competing_resubmission_exists(
        self, mock_get, mock_exclude
    ):
        class MockCurrentSAC:
            report_id = "R4"
            resubmission_meta = {
                "version": 2,
                "previous_report_id": "P1",
                "resubmission_status": "most_recent",
            }

        class MockQuerySet(list):
            def exclude(self, **kwargs):
                return self

        mock_get.return_value = MockCurrentSAC()
        mock_exclude.return_value = MockQuerySet([])

        sac_data = {
            "sf_sac_meta": {"report_id": "R4"},
            "sf_sac_sections": {},
        }

        result = check_parent_resubmission_conflict(sac_data)

        self.assertEqual(result, [])

    @patch("audit.models.SingleAuditChecklist.objects.exclude")
    @patch("audit.models.SingleAuditChecklist.objects.get")
    def test_returns_friendly_error_when_competing_resubmission_exists(
        self, mock_get, mock_exclude
    ):
        class MockCurrentSAC:
            report_id = "R5"
            resubmission_meta = {
                "version": 2,
                "previous_report_id": "P2",
                "resubmission_status": "most_recent",
            }

        class MockSiblingSAC:
            report_id = "R6"
            resubmission_meta = {
                "version": 2,
                "previous_report_id": "P2",
                "resubmission_status": "most_recent",
            }

        class MockOtherSAC:
            report_id = "R7"
            resubmission_meta = {
                "version": 2,
                "previous_report_id": "P3",
                "resubmission_status": "most_recent",
            }

        class MockQuerySet(list):
            def exclude(self, **kwargs):
                return self

        mock_get.return_value = MockCurrentSAC()
        mock_exclude.return_value = MockQuerySet([MockSiblingSAC(), MockOtherSAC()])

        sac_data = {
            "sf_sac_meta": {"report_id": "R5"},
            "sf_sac_sections": {},
        }

        result = check_parent_resubmission_conflict(sac_data)

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
