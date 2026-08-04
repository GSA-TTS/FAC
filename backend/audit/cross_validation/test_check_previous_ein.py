from datetime import date

from django.test import TestCase
from model_bakery import baker

from audit.cross_validation.check_previous_ein import check_previous_ein
from dissemination.models import General


class TestCheckPreviousEin(TestCase):
    def build_sac(self, uei="TEST_UEI", ein="12-3456789"):
        return {
            "sf_sac_sections": {
                "general_information": {
                    "auditee_uei": uei,
                    "ein": ein,
                }
            }
        }

    def test_no_warning_when_no_previous_submission(self):
        self.assertEqual(check_previous_ein(self.build_sac()), [])

    def test_no_warning_when_ein_matches_previous_submission(self):
        baker.make(
            General,
            report_id="2025-09-GSAFAC-0000000001",
            auditee_uei="TEST_UEI",
            auditee_ein="12-3456789",
            fac_accepted_date=date(2025, 1, 1),
            fy_end_date=date(2025, 9, 30),
            audit_year="2025",
        )

        result = check_previous_ein(self.build_sac())

        self.assertEqual(result, [])

    def test_warning_when_ein_does_not_match_previous_submission(self):
        previous_report_id = "2025-09-GSAFAC-0000000001"

        baker.make(
            General,
            report_id=previous_report_id,
            auditee_uei="TEST_UEI",
            auditee_ein="12-3456789",
            fac_accepted_date=date(2025, 1, 1),
            fy_end_date=date(2025, 9, 30),
            audit_year="2025",
        )

        result = check_previous_ein(self.build_sac(ein="98-7654321"))

        self.assertEqual(len(result), 1)
        self.assertIn("warning", result[0])
        self.assertIn(previous_report_id, result[0]["warning"])
        self.assertIn("12-3456789", result[0]["warning"])
        self.assertIn("98-7654321", result[0]["warning"])

    def test_uses_most_recent_accepted_submission(self):
        older_report_id = "2024-09-GSAFAC-0000000001"
        newest_report_id = "2025-09-GSAFAC-0000000002"

        baker.make(
            General,
            report_id=older_report_id,
            auditee_uei="TEST_UEI",
            auditee_ein="11-1111111",
            fac_accepted_date=date(2024, 1, 1),
            fy_end_date=date(2024, 9, 30),
            audit_year="2024",
        )

        baker.make(
            General,
            report_id=newest_report_id,
            auditee_uei="TEST_UEI",
            auditee_ein="22-2222222",
            fac_accepted_date=date(2025, 1, 1),
            fy_end_date=date(2025, 9, 30),
            audit_year="2025",
        )

        result = check_previous_ein(self.build_sac(ein="98-7654321"))

        self.assertEqual(len(result), 1)
        self.assertIn(newest_report_id, result[0]["warning"])
        self.assertIn("22-2222222", result[0]["warning"])
        self.assertNotIn(older_report_id, result[0]["warning"])
        self.assertNotIn("11-1111111", result[0]["warning"])

    def test_does_not_warn_for_different_uei(self):
        baker.make(
            General,
            report_id="2025-09-GSAFAC-0000000001",
            auditee_uei="OTHER_UEI",
            auditee_ein="12-3456789",
            fac_accepted_date=date(2025, 1, 1),
            fy_end_date=date(2025, 9, 30),
            audit_year="2025",
        )

        result = check_previous_ein(
            self.build_sac(
                uei="TEST_UEI",
                ein="98-7654321",
            )
        )

        self.assertEqual(result, [])
