from django.test import SimpleTestCase
from audit.intakelib.checks.check_uei_match import verify_auditee_uei_match


class TestVerifyAuditeeUEIMatch(SimpleTestCase):
    def setUp(self):
        self.ir = [
            {
                "name": "Coversheet",
                "ranges": [
                    {
                        "end_cell": {"column": "A", "row": "1"},
                        "name": "auditee_uei",
                        "start_cell": {"column": "A", "row": "1"},
                        "values": ["AB3KNQ123PH9"],
                    },
                ],
            }
        ]
        self.matching_uei = "AB3KNQ123PH9"
        self.unmatched_uei = "XYZ7RJTP7315"

    def test_uei_match(self):
        """Test case where UEIs match."""
        result = verify_auditee_uei_match(self.ir, self.matching_uei)
        self.assertIsNone(result)

    def test_uei_mismatch(self):
        """Test case where UEIs do not match."""
        result = verify_auditee_uei_match(self.ir, self.unmatched_uei)
        self.assertIsNotNone(result)
