from django.test import SimpleTestCase
from audit.intakelib.checks.check_passthrough_names_and_ids_uniqueness import (
    passthrough_names_and_ids_uniqueness,
)


class TestPassthroughNamesAndIDsUniqueness(SimpleTestCase):
    def setUp(self):
        self.ir = [
            {
                "name": "Form",
                "ranges": [
                    {
                        "end_cell": {"column": "A", "row": "3"},
                        "name": "passthrough_name",
                        "start_cell": {"column": "A", "row": "1"},
                        "values": ["name", "name1|name2", "other_name"],
                    },
                    {
                        "end_cell": {"column": "C", "row": "3"},
                        "name": "passthrough_identifying_number",
                        "start_cell": {"column": "C", "row": "1"},
                        "values": ["id", "id1|id2", "other_id"],
                    },
                ],
            }
        ]

    def test_unique_names_and_ids(self):
        """Test that unique names and IDs should not raise any errors."""
        errors = passthrough_names_and_ids_uniqueness(self.ir)
        self.assertEqual(
            len(errors), 0, "Should not find any errors with unique names and IDs"
        )

    def test_duplicate_names_and_ids(self):
        """Test that duplicate names and IDs should raise errors."""
        self.ir[0]["ranges"][0]["values"].append("name2")
        self.ir[0]["ranges"][1]["values"].append("id2")
        errors = passthrough_names_and_ids_uniqueness(self.ir)
        self.assertNotEqual(
            len(errors), 0, "Should find errors with duplicate names and IDs"
        )

    def test_missing_names_or_ids(self):
        """Test that empty names and IDs should not raise any errors."""
        self.ir[0]["ranges"][0]["values"].append("")
        self.ir[0]["ranges"][0]["values"].append("")
        errors = passthrough_names_and_ids_uniqueness(self.ir)
        self.assertEqual(
            len(errors), 0, "Should not find errors with empty names or IDs"
        )
