import unittest
from django.test import SimpleTestCase

from audit.intakelib.checks.check_finding_uniqueness import check_finding_uniqueness


@unittest.skip(
    "Skipping while finding uniqueness is disabled, see ticket #4385 for more information."
)
class TestCheckFindingUniqueness(SimpleTestCase):
    def setUp(self):
        self.ir = [
            {
                "name": "Form",
                "ranges": [
                    {
                        "name": "reference_number",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "20001"},
                        "values": ["FR1", "FR1", "FR2"],
                    },
                    {
                        "name": "compliance_requirement",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "2"},
                        "values": ["CR1", "CR1", "CR2"],
                    },
                    {
                        "name": "modified_opinion",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "2"},
                        "values": ["MO1", "MO1", "MO2"],
                    },
                    {
                        "name": "other_matters",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "20001"},
                        "values": ["OM1", "OM1", "OM2"],
                    },
                    {
                        "name": "material_weakness",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "2"},
                        "values": ["MW1", "MW1", "MW2"],
                    },
                    {
                        "name": "significant_deficiency",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "20001"},
                        "values": ["SD1", "SD1", "SD2"],
                    },
                    {
                        "name": "other_findings",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "2"},
                        "values": ["OF1", "OF1", "OF2"],
                    },
                    {
                        "name": "questioned_costs",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "20001"},
                        "values": ["QC1", "QC1", "QC2"],
                    },
                    {
                        "name": "repeat_prior_reference",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "2"},
                        "values": ["RR1", "RR1", "RR2"],
                    },
                    {
                        "name": "prior_references",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "20001"},
                        "values": ["PR1", "PR1", "PR2"],
                    },
                ],
            }
        ]

    def test_unique_finding_success(self):
        """
        Test case where all findings are unique for each reference.
        """
        errors = check_finding_uniqueness(self.ir)
        self.assertEqual(errors, [])

    def test_duplicate_finding_reference(self):
        """
        Test case where a finding reference has multiple different findings associated with it.
        """
        # Modify the finding sets to simulate a mismatch for FR1
        self.ir[0]["ranges"][6]["values"] = [
            "OF1",
            "OF2",
            "OF2",
        ]  # Change in `other_findings`

        errors = check_finding_uniqueness(self.ir)

        # Expect an error for FR1 due to different findings in rows 0 and 1
        self.assertEqual(len(errors), 1)
        self.assertIn("On row", errors[0][3]["text"])

    def test_gsa_migration(self):
        """
        Test case where is_gsa_migration is True and no errors should be returned.
        """
        errors = check_finding_uniqueness(self.ir, is_gsa_migration=True)
        self.assertEqual(errors, [])
