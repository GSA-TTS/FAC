from django.test import SimpleTestCase
from copy import deepcopy
from audit.intakelib.intermediate_representation import (
    extract_workbook_as_ir,
    ranges_to_rows,
    remove_null_rows,
)
from unittest.mock import MagicMock, patch
from django.core.exceptions import ValidationError


class IRTests(SimpleTestCase):
    s1 = {
        "ranges": [
            {
                "values": [1, 2, 3, None, None],
            },
            {
                "values": ["a", "b", "c", None, None],
            },
            {
                "values": [8, None, 10, None, None],
            },
        ]
    }

    s2 = {
        "ranges": [
            {
                "values": [1, None, None, None, None],
            },
            {
                "values": ["a", "b", "c", None, None],
            },
            {
                "values": [8, None, 10, None, None],
            },
        ]
    }

    r1 = {
        "ranges": [
            {
                "values": [1, 2, 3],
            },
            {
                "values": ["a", "b", "c"],
            },
            {
                "values": [8, None, 10],
            },
        ]
    }

    r2 = {
        "ranges": [
            {
                "values": [1, None, None],
            },
            {
                "values": ["a", "b", "c"],
            },
            {
                "values": [8, None, 10],
            },
        ]
    }

    def test_ranges_to_rows(self):
        self.assertEqual(
            [[1, "a", 8], [2, "b", None], [3, "c", 10]],
            ranges_to_rows(IRTests.s1["ranges"]),
        )

        self.assertEqual(
            [[1, "a", 8], [None, "b", None], [None, "c", 10]],
            ranges_to_rows(IRTests.s2["ranges"]),
        )

    def test_remove_null_rows(self):
        cp = deepcopy(IRTests.s1)
        remove_null_rows(cp)
        self.assertEqual(cp, IRTests.r1)

        cp = deepcopy(IRTests.s2)
        remove_null_rows(cp)
        self.assertEqual(cp, IRTests.r2)


class TestExtractWorkbookAsIr(SimpleTestCase):
    def setUp(self):
        """Common setup for all tests."""
        self.destinations = iter([("Sheet1", "$A$1:$A$10")])
        self.test_range_mock = MagicMock(
            attr_text="Sheet1!$A$1:$A$10",
            destinations=self.destinations,
        )
        self.test_range_mock.name = "TestRange"

        self.mock_workbook = MagicMock()
        self.mock_workbook.__getitem__.return_value = MagicMock()  # Default mock sheet
        self.mock_workbook.defined_names = {"TestRange": self.test_range_mock}

    @patch("audit.intakelib.intermediate_representation._open_workbook")
    def test_extract_with_valid_input(self, mock_open_workbook):
        """Test that the function returns the expected intermediate representation."""

        mock_open_workbook.return_value = self.mock_workbook

        # expected result is: [{'name': 'Sheet1', 'ranges': [{'name': 'TestRange', 'start_cell': {'column': 'A', 'row': '1'}, 'end_cell': {'column': 'A', 'row': '0'}, 'values': []}]}]
        result = extract_workbook_as_ir("dummy_file_path")

        # Assertions
        mock_open_workbook.assert_called_with("dummy_file_path")
        self.assertIsInstance(result, list)
        self.assertGreaterEqual(len(result), 1)

        sheet_info = result[0]
        self.assertIn("name", sheet_info)
        self.assertEqual(sheet_info["name"], "Sheet1")

        self.assertIn("ranges", sheet_info)
        self.assertIsInstance(sheet_info["ranges"], list)
        self.assertGreaterEqual(len(sheet_info["ranges"]), 1)

        range_info = sheet_info["ranges"][0]
        self.assertEqual(range_info["name"], "TestRange")

        self.assertEqual(range_info["start_cell"], {"column": "A", "row": "1"})
        # End cell row is the last cell with a value.
        # In this case End cell is 0 as there is no value associated with the range
        self.assertEqual(range_info["end_cell"], {"column": "A", "row": "0"})

        # Validate values list within the range
        self.assertEqual(range_info["values"], [])

    @patch("audit.intakelib.intermediate_representation._open_workbook")
    def test_extract_with_ref_error(self, mock_open_workbook):
        """Test handling of a workbook with a #REF! error."""
        # Modify test_range_mock for this specific test
        self.test_range_mock.attr_text = "#REF!"
        mock_open_workbook.return_value = self.mock_workbook

        with self.assertRaises(ValidationError):
            extract_workbook_as_ir("dummy_file_with_ref_error")

    @patch("audit.intakelib.intermediate_representation._open_workbook")
    def test_no_destination_found(self, mock_open_workbook):
        """Test handling of a workbook with no destinations found for a named range."""
        self.destinations = iter([])
        self.test_range_mock.destinations = self.destinations
        mock_open_workbook.return_value = self.mock_workbook
        with self.assertRaises(ValidationError):
            extract_workbook_as_ir("dummy_file_with_malformed_attr_text")
