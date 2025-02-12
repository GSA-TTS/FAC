from unittest.mock import Mock

from django.test import SimpleTestCase
from django.core.exceptions import ValidationError

from audit.intakelib.checks.check_aln_is_valid import aln_is_valid
from audit.context import set_sac_to_context

class TestAlnIsValid(SimpleTestCase):
    def setUp(self):
        self.ir = [
            {
                # User-supplied ALNs (prefix.extension)
                "name": "Form",
                "ranges": [
                    {
                        "name": "federal_agency_prefix",
                        "start_cell": {"column": "B", "row": "2"},
                        "end_cell": {"column": "B", "row": "20001"},
                        "values": ["93"],
                    },
                    {
                        "name": "three_digit_extension",
                        "start_cell": {"column": "C", "row": "2"},
                        "end_cell": {"column": "C", "row": "20001"},
                        "values": ["001"],
                    },
                ],
            },
            {
                # ALNs that are considered valid
                "name": "FederalPrograms",
                "ranges": [
                    {
                        "name": "federal_program_name_lookup",
                        "start_cell": {"column": "A", "row": "2"},
                        "end_cell": {"column": "A", "row": "20001"},
                        "values": ["Foo Program Name"],
                    },
                    {
                        "name": "aln_lookup",
                        "start_cell": {"column": "B", "row": "2"},
                        "end_cell": {"column": "B", "row": "20001"},
                        "values": ["93.001"],
                    },
                ],
            },
        ]
        self.mock_sac = Mock()

    def test_valid_aln(self):
        """
        Normal case where a valid ALN is supplied
        """
        with set_sac_to_context(self.mock_sac):
            errors = aln_is_valid(self.ir)

            self.assertEqual(errors, None)

    def test_invalid_aln(self):
        """
        Error case where invalid ALN is supplied
        """
        # No ALNs are considered valid
        self.ir[1]["ranges"][1]["values"] = []

        with set_sac_to_context(None):
            with self.assertRaises(ValidationError) as context:
                aln_is_valid(self.ir)

            error = context.exception.args[0][0]
            self.assertEqual(
                error[3]["text"],
                "The ALN provided, 93.001, does not match any in the FederalPrograms sheet",
            )
