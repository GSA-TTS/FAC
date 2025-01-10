from unittest.mock import Mock
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from audit.intakelib.checks.check_finding_reference_year import finding_reference_year
from audit.context import set_sac_to_context


class TestFindingReferenceYear(SimpleTestCase):
    def setUp(self):
        self.ir = [
            {
                "name": "Form",
                "ranges": [
                    {
                        "name": "reference_number",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "20001"},
                        "values": ["2022-001", "2022-002", "2022-003"],
                    },
                ],
            }
        ]
        self.mock_sac = Mock()

    def test_success(self):
        """
        Test case where all finding reference years match the audit year.
        """
        self.mock_sac.general_information = {"auditee_fiscal_period_end": "2022-12-31"}
        with set_sac_to_context(self.mock_sac):

            errors = finding_reference_year(self.ir)

            self.assertEqual(errors, None)

    def test_mismatched_years(self):
        """
        Test case where finding reference years do not match the audit year.
        """
        self.mock_sac.general_information = {"auditee_fiscal_period_end": "2023-12-31"}
        with set_sac_to_context(self.mock_sac):
            with self.assertRaises(ValidationError) as context:
                finding_reference_year(self.ir)

        errors = context.exception.args[0]
        self.assertEqual(len(errors), 3)  # Three mismatches
        self.assertIn("2022-001", errors[0][3]["text"])
        self.assertIn("2022-002", errors[1][3]["text"])
        self.assertIn("2022-003", errors[2][3]["text"])

    def test_gsa_migration(self):
        """
        Test case where is_gsa_migration is True and no validation is performed.
        """
        errors = finding_reference_year(self.ir, is_gsa_migration=True)

        self.assertEqual(errors, [])
