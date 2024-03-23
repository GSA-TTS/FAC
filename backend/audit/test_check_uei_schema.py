from django.conf import settings
from django.test import SimpleTestCase
from audit.intakelib.checks.check_uei_schema import verify_auditee_uei_schema


class TestVerifyAuditeeUEISchema(SimpleTestCase):
    def setUp(self):
        self.ir = [
            {
                "name": "Coversheet",
                "ranges": [
                    {
                        "end_cell": {"column": "A", "row": "1"},
                        "name": "auditee_uei",
                        "start_cell": {"column": "A", "row": "1"},
                        "values": ["AB3KNQ123PH9"],  # valid UEI schema
                    },
                ],
            }
        ]

    def test_verify_auditee_uei_schema_success(self):
        """Test that the function should not return any errors."""
        result = verify_auditee_uei_schema(self.ir)
        self.assertIsNone(result)

    def test_verify_auditee_uei_invalid_length(self):
        """Test handling an invalid UEI length."""
        self.ir[0]["ranges"][0]["values"] = ["AB3KNQ123PH"]  # Invalid length
        result = verify_auditee_uei_schema(self.ir)
        self.assertIsNotNone(result)

    def test_verify_auditee_uei_invalid_pattern(self):
        """Test handling an invalid UEI pattern."""
        self.ir[0]["ranges"][0]["values"] = ["!@#$%^&*()_+"]  # Invalid characters
        result = verify_auditee_uei_schema(self.ir)
        self.assertIsNotNone(result)

    def test_verify_auditee_uei_special_migration(self):
        """Test handling the special 'GSA_MIGRATION' string."""
        self.ir[0]["ranges"][0]["values"] = [settings.GSA_MIGRATION]  # Special string
        result = verify_auditee_uei_schema(self.ir)
        self.assertIsNone(result)
