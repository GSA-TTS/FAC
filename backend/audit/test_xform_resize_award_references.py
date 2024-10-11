from unittest.mock import patch

from django.test import SimpleTestCase

from audit.intakelib.transforms.xform_resize_award_references import (
    _format_reference,
    resize_award_reference,
)


class TestResizeAwardReference(SimpleTestCase):

    @patch("audit.intakelib.transforms.xform_resize_award_references.get_range_by_name")
    @patch(
        "audit.intakelib.transforms.xform_resize_award_references.replace_range_by_name"
    )
    def test_resize_award_reference(
        self, mock_replace_range_by_name, mock_get_range_by_name
    ):
        """Test the resize_award_reference function"""
        ir = []
        references = {
            "values": [
                "AWARD-123",  # Will need padding
                "AWARD-4567",  # Will need padding
                "AWARD-12345",  # Correct length, no padding
                None,  # No change for None
            ]
        }
        expected_new_values = [
            "AWARD-00123",
            "AWARD-04567",
            "AWARD-12345",
            None,
        ]

        mock_get_range_by_name.return_value = references
        new_ir = resize_award_reference(ir)

        mock_get_range_by_name.assert_called_once_with(ir, "award_reference")
        mock_replace_range_by_name.assert_called_once_with(
            ir, "award_reference", expected_new_values
        )

        self.assertEqual(new_ir, mock_replace_range_by_name.return_value)

    def test_format_reference(self):
        """Test the _format_reference function"""
        self.assertEqual(_format_reference("AWARD-123"), "AWARD-00123")
        self.assertEqual(_format_reference("AWARD-4567"), "AWARD-04567")
        self.assertEqual(_format_reference("AWARD-12345"), "AWARD-12345")
        self.assertEqual(_format_reference(None), None)
        self.assertEqual(_format_reference(""), "")
