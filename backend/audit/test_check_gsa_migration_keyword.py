import random
from django.forms import ValidationError
from django.test import SimpleTestCase

from .intakelib.checks.check_gsa_migration_keyword import (
    check_for_gsa_migration_keyword,
)


class TestCheckForGsaMigrationKeyword(SimpleTestCase):
    def setUp(self):
        self.range_names = [
            "auditee_uei",
            "three_digit_extension",
            "additional_award_identification",
        ]
        self.ir_with_gsa_migration_keyword = [
            {
                "name": "Sheet1",
                "ranges": [
                    {
                        "name": random.choice(self.range_names),
                        "start_cell": {"column": "A", "row": "1"},
                        "end_cell": {"column": "A", "row": "4"},
                        "values": [
                            "SOME_VALUE",
                            "GSA_MIGRATION",
                            "GSA_MIGRATION",
                            "SOME_OTHER_VALUE",
                        ],
                    },
                ],
            },
        ]
        self.ir_without_gsa_migration_keyword = [
            {
                "name": "Sheet1",
                "ranges": [
                    {
                        "name": random.choice(self.range_names),
                        "start_cell": {"column": "A", "row": "1"},
                        "end_cell": {"column": "A", "row": "3"},
                        "values": [
                            "SOME_VALUE",
                            "SOME_OTHER_VALUE",
                            "MORE_VALUE",
                        ],
                    },
                ],
            },
        ]

    def test_for_ir_with_gsa_migration_keyword(self):
        """Test that the function returns a validation error when `GSA_MIGRATION` keyword is encountered."""
        with self.assertRaises(ValidationError):
            check_for_gsa_migration_keyword(self.ir_with_gsa_migration_keyword)

    def test_for_ir_without_gsa_migration_keyword(self):
        """Test that the function returns no errors when no `GSA_MIGRATION` keyword is encountered."""
        self.assertEqual(
            check_for_gsa_migration_keyword(self.ir_without_gsa_migration_keyword),
            None,
        )
