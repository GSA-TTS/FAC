from django.test import SimpleTestCase
from .utils import Util


class TestRemoveExtraFields(SimpleTestCase):
    def setUp(self):
        self.data = {
            "auditor_country": "USA",
            "auditor_address_line_1": "123 Main St",
            "auditor_city": "Anytown",
            "auditor_state": "CA",
            "auditor_zip": "90210",
            "auditor_international_address": "",
            "audit_period_covered": "biennial",
            "audit_period_other_months": "",
        }

    def test_remove_international_address_for_usa_without_address(self):
        result = Util.remove_extra_fields(self.data)
        self.assertNotIn("auditor_international_address", result)

    def test_remove_usa_address_fields_for_non_usa_without_usa_address_fields(self):
        # Non provided fields are returned as empty strings from the form
        self.data["auditor_address_line_1"] = ""
        self.data["auditor_city"] = ""
        self.data["auditor_state"] = ""
        self.data["auditor_zip"] = ""
        self.data["auditor_country"] = "non-USA"
        self.data["auditor_international_address"] = "123 International St"
        result = Util.remove_extra_fields(self.data)
        self.assertNotIn("auditor_zip", result)
        self.assertNotIn("auditor_state", result)
        self.assertNotIn("auditor_address_line_1", result)
        self.assertNotIn("auditor_city", result)

    def test_remove_audit_period_other_months_when_not_other(self):
        result = Util.remove_extra_fields(self.data)
        self.assertNotIn("audit_period_other_months", result)

