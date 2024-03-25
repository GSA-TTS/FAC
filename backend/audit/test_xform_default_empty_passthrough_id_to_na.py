from django.conf import settings
from django.test import SimpleTestCase

from audit.intakelib.transforms.xform_fill_missing_passthrough_ids_with_na import (
    fill_missing_passthrough_ids_with_na,
)


class TestDefaultEmptyPassthroughIdToNa(SimpleTestCase):
    def setUp(self):
        self.ir = [
            {
                "name": "Form",
                "ranges": [
                    {"name": "is_direct", "values": ["Y", "N", "N", "Y"]},
                    {"name": "passthrough_name", "values": ["", "name2", "name3", ""]},
                    {
                        "name": "passthrough_identifying_number",
                        "values": ["", "id2", "id3", ""],
                    },
                ],
            }
        ]

    def test_ids_present(self):
        """Test that IDs should remain unchanged when present."""
        xform_ir = fill_missing_passthrough_ids_with_na(self.ir)
        expected_ids = ["", "id2", "id3", ""]
        self.assertEqual(
            xform_ir[0]["ranges"][2]["values"],
            expected_ids,
            "IDs should remain unchanged when present",
        )

    def test_default_missing_ids_to_na(self):
        """Test that missing IDs for non-direct awards should be defaulted to N/A."""
        self.ir[0]["ranges"][2]["values"][1] = ""

        expected_ids = ["", settings.NOT_APPLICABLE, "id3", ""]

        xform_ir = fill_missing_passthrough_ids_with_na(self.ir)
        self.assertEqual(
            xform_ir[0]["ranges"][2]["values"],
            expected_ids,
            "Missing IDs for non-direct awards should be defaulted to N/A",
        )

    def test_ignore_direct_awards(self):
        """Test that direct awards with missing IDs should be ignored."""
        self.ir[0]["ranges"][1]["values"][0] = "name1"
        xform_ir = fill_missing_passthrough_ids_with_na(self.ir)
        self.assertNotEqual(
            xform_ir[0]["ranges"][1]["values"][0],
            "",
            "Direct awards with missing IDs should be ignored",
        )
