from django.forms import ValidationError
from django.test import SimpleTestCase

from audit.intakelib.checks.check_data_row_range_in_form_sheet import validate_ranges


class TestValidateDataRowRangeInFormSheet(SimpleTestCase):
    def setUp(self):
        self.valid_ir_v105 = [
            {
                "name": "Form",
                "ranges": [
                    {
                        "name": "data_range",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "10001"},
                        "values": [],
                    },
                ],
            },
            {
                "name": "Coversheet",
                "ranges": [
                    {
                        "name": "version",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "2"},
                        "values": ["1.0.5"],
                    }
                ],
            },
        ]

        self.valid_ir_v110 = [
            {
                "name": "Form",
                "ranges": [
                    {
                        "name": "version",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "2"},
                        "values": ["1.1.0"],
                    },
                    {
                        "name": "data_range",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "20001"},
                        "values": [],
                    },
                ],
            }
        ]

    def test_valid_data_range_v105(self):
        """Test that the function returns no errors when the data is within the allowed range for version 1.0.5."""
        validate_ranges(self.valid_ir_v105)

    def test_invalid_data_v105(self):
        """Test that the function returns a validation error when the data exceeds the allowed range for version 1.0.5."""
        self.valid_ir_v105[0]["ranges"][0]["end_cell"] = self.valid_ir_v105[0][
            "ranges"
        ][0]["end_cell"] | {
            "row": "10002",
        }
        with self.assertRaises(ValidationError):
            validate_ranges(self.valid_ir_v105)

    def test_valid_data_v110(self):
        """Test that the function returns no errors when the data is within the allowed range for version 1.1.0."""
        validate_ranges(self.valid_ir_v110)

    def test_invalid_data_v110(self):
        """Test that the function returns a validation error when the data exceeds the allowed range for version 1.1.0."""
        self.valid_ir_v110[0]["ranges"][1]["end_cell"] = self.valid_ir_v110[0][
            "ranges"
        ][1]["end_cell"] | {
            "row": "20002",
        }
        with self.assertRaises(ValidationError):
            validate_ranges(self.valid_ir_v110)
