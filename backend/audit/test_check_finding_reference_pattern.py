from audit.intakelib.checks.check_finding_reference_pattern import (
    finding_reference_pattern,
)

from django.conf import settings
from django.test import SimpleTestCase
from django.core.exceptions import ValidationError


class TestFindingReferencePattern(SimpleTestCase):
    def setUp(self):
        self.ir = [
            {
                "name": "Form",
                "ranges": [
                    {
                        "name": "reference_number",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "20001"},
                        "values": ["2022-001"],
                    },
                ],
            }
        ]
        self.expected_error = [
            (
                "A",
                2,
                "Form",
                {
                    "text": "Finding references must be in the format <b>20##-###</b> where the first four digits are a year after 2010, for example, <b>2019-001, 2019-002</b>",
                    "link": "Intake checks: no link defined",
                },
            ),
        ]

    def test_success(self):
        """Standard valid reference passes"""
        errors = finding_reference_pattern(self.ir)

        self.assertEqual(errors, None)

    def test_bad_format(self):
        """Poorly formatted reference errors"""
        self.ir[0]["ranges"][0]["values"] = ["bad-format"]

        with self.assertRaises(ValidationError) as context:
            finding_reference_pattern(self.ir)

        self.assertEqual(
            context.exception.args[0],
            self.expected_error,
        )

    def test_empty(self):
        """Empty reference passes"""
        self.ir[0]["ranges"][0]["values"] = [""]

        errors = finding_reference_pattern(self.ir)

        self.assertEqual(errors, None)

    def test_valid_gsa_migration(self):
        """Valid GSA migration passes"""
        self.ir[0]["ranges"][0]["values"] = [settings.GSA_MIGRATION]

        errors = finding_reference_pattern(self.ir, is_gsa_migration=True)

        self.assertEqual(errors, None)

    def test_invalid_gsa_migration(self):
        """Invalid GSA migration errors"""
        self.ir[0]["ranges"][0]["values"] = [settings.GSA_MIGRATION]

        with self.assertRaises(ValidationError) as context:
            finding_reference_pattern(self.ir, is_gsa_migration=False)

        self.assertEqual(
            context.exception.args[0],
            self.expected_error,
        )
