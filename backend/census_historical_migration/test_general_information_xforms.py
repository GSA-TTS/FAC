from datetime import datetime, timedelta
from django.conf import settings
from django.test import SimpleTestCase

from .sac_general_lib.general_information import (
    AUDIT_TYPE_DICT,
    PERIOD_DICT,
    xform_audit_period_covered,
    xform_audit_type,
    xform_auditee_fiscal_period_end,
    xform_auditee_fiscal_period_start,
    xform_country,
    xform_entity_type,
    xform_replace_empty_auditor_email,
)
from .exception_utils import (
    DataMigrationError,
    DataMigrationValueError,
)


class TestXformEntityType(SimpleTestCase):
    def test_valid_phrases(self):
        """Test that the function returns the correct results when given valid phrases."""
        self.assertEqual(
            xform_entity_type("institution of higher education"), "higher-ed"
        )
        self.assertEqual(xform_entity_type("nonprofit"), "non-profit")
        self.assertEqual(xform_entity_type("Non-Profit"), "non-profit")
        self.assertEqual(xform_entity_type("local government"), "local")
        self.assertEqual(xform_entity_type("state"), "state")
        self.assertEqual(xform_entity_type("unknown"), "unknown")
        self.assertEqual(xform_entity_type("tribe"), "tribal")
        self.assertEqual(xform_entity_type("tribal"), "tribal")

    def test_valid_phrases_with_extra_whitespace(self):
        """Test that the function returns the correct results when given valid phrases with extra whitespace."""
        self.assertEqual(
            xform_entity_type("institution of higher education "), "higher-ed"
        )
        self.assertEqual(xform_entity_type(" nonprofit "), "non-profit")
        self.assertEqual(xform_entity_type("Non-Profit "), "non-profit")
        self.assertEqual(xform_entity_type(" local government "), "local")
        self.assertEqual(xform_entity_type(" state   "), "state")

    def test_valid_phrases_with_extra_whitespace_with_capitalization(self):
        """Test that the function returns the correct results when given valid phrases with extra whitespace and upper cases."""
        self.assertEqual(
            xform_entity_type("Institution of Higher Education "), "higher-ed"
        )
        self.assertEqual(xform_entity_type(" Nonprofit "), "non-profit")
        self.assertEqual(xform_entity_type("Non-Profit "), "non-profit")
        self.assertEqual(xform_entity_type(" LOCAL Government "), "local")
        self.assertEqual(xform_entity_type(" STATE   "), "state")
        self.assertEqual(xform_entity_type(" Tribal   "), "tribal")

    def test_valid_phrases_with_extra_whitespace_with_extra_words_with_capitalization(
        self,
    ):
        """Test that the function returns the correct results when given valid phrases with extra whitespace and extra words."""
        self.assertEqual(
            xform_entity_type("Institution of Higher Education (IHE) and Research"),
            "higher-ed",
        )

        self.assertEqual(
            xform_entity_type(" LOCAL GOVERNMENT AND AGENCIES "),
            "local",
        )
        self.assertEqual(
            xform_entity_type(" STATE and Non-Governmental Organization   "), "state"
        )
        self.assertEqual(
            xform_entity_type(" Indian tribe or Tribal  Organization   "), "tribal"
        )

    def test_invalid_phrase(self):
        """Test that the function raises an exception when given an invalid phrase."""
        with self.assertRaises(DataMigrationError):
            xform_entity_type("business")

    def test_empty_string(self):
        """Test that the function raises an exception when given an empty string."""
        with self.assertRaises(DataMigrationError):
            xform_entity_type("")

    def test_none_input(self):
        """Test that the function raises an exception when given None."""
        with self.assertRaises(DataMigrationError):
            xform_entity_type(None)


class TestXformCountry(SimpleTestCase):
    class MockAuditHeader:
        def __init__(self, CPASTATE):
            self.CPASTATE = CPASTATE

    def setUp(self):
        self.general_information = {
            "auditor_country": "",
        }
        self.audit_header = self.MockAuditHeader("")

    def test_when_auditor_country_set_to_us(self):
        """Test that the function returns the correct results when the auditor country is set to US."""
        self.general_information["auditor_country"] = "US"
        result = xform_country(self.general_information, self.audit_header)
        self.assertEqual(result["auditor_country"], "USA")

    def test_when_auditor_country_set_to_usa(self):
        """Test that the function returns the correct results when the auditor country is set to USA."""
        self.general_information["auditor_country"] = "USA"
        result = xform_country(self.general_information, self.audit_header)
        self.assertEqual(result["auditor_country"], "USA")

    def test_when_auditor_country_set_to_empty_string_and_auditor_state_valid(self):
        """Test that the function returns the correct results when the auditor country is set to an empty string."""
        self.general_information["auditor_country"] = ""
        self.audit_header.CPASTATE = "MA"
        result = xform_country(self.general_information, self.audit_header)
        self.assertEqual(result["auditor_country"], "USA")

    def test_when_auditor_country_set_to_empty_string_and_auditor_state_invalid(self):
        """Test that the function raises an exception when the auditor country is set to an empty string and the auditor state is invalid."""
        self.general_information["auditor_country"] = ""
        self.audit_header.CPASTATE = "XX"
        with self.assertRaises(DataMigrationError):
            xform_country(self.general_information, self.audit_header)


class TestXformAuditeeFiscalPeriodEnd(SimpleTestCase):
    def setUp(self):
        self.general_information = {
            "auditee_fiscal_period_end": "01/31/2021 00:00:00",
        }

    def test_when_auditee_fiscal_period_end_is_valid(self):
        """Test that the function returns the correct results when the fiscal period end is valid."""
        result = xform_auditee_fiscal_period_end(self.general_information)
        self.assertEqual(result["auditee_fiscal_period_end"], "2021-01-31")

    def test_when_auditee_fiscal_period_end_is_invalid(self):
        """Test that the function raises an exception when the fiscal period end is invalid."""
        self.general_information["auditee_fiscal_period_end"] = "01/31/2021"
        with self.assertRaises(DataMigrationValueError):
            xform_auditee_fiscal_period_end(self.general_information)
        self.general_information["auditee_fiscal_period_end"] = ""
        with self.assertRaises(DataMigrationError):
            xform_auditee_fiscal_period_end(self.general_information)


class TestXformAuditeeFiscalPeriodStart(SimpleTestCase):
    def setUp(self):
        self.general_information = {
            "auditee_fiscal_period_end": "01/31/2021 00:00:00",
        }

    def test_when_auditee_fiscal_period_end_is_valid(self):
        """Test that the function returns the correct results when the fiscal period end is valid."""
        result = xform_auditee_fiscal_period_start(self.general_information)
        expected_date = (
            datetime.strptime(
                self.general_information["auditee_fiscal_period_end"],
                "%m/%d/%Y %H:%M:%S",
            )
            - timedelta(days=365)
        ).strftime("%Y-%m-%d")
        self.assertEqual(result["auditee_fiscal_period_start"], expected_date)

    def test_when_auditee_fiscal_period_end_is_invalid(self):
        """Test that the function raises an exception when the fiscal period end is invalid."""
        self.general_information["auditee_fiscal_period_end"] = "01/31/2021"
        with self.assertRaises(DataMigrationValueError):
            xform_auditee_fiscal_period_start(self.general_information)
        self.general_information["auditee_fiscal_period_end"] = ""
        with self.assertRaises(DataMigrationValueError):
            xform_auditee_fiscal_period_start(self.general_information)


class TestXformAuditPeriodCovered(SimpleTestCase):
    def test_valid_period(self):
        for key, value in PERIOD_DICT.items():
            with self.subTest(key=key):
                general_information = {"audit_period_covered": key}
                result = xform_audit_period_covered(general_information)
                self.assertEqual(result["audit_period_covered"], value)

    def test_invalid_period(self):
        general_information = {"audit_period_covered": "invalid_key"}
        with self.assertRaises(DataMigrationError):
            xform_audit_period_covered(general_information)

    def test_missing_period(self):
        general_information = {}
        with self.assertRaises(DataMigrationError):
            xform_audit_period_covered(general_information)


class TestXformAuditType(SimpleTestCase):
    def test_valid_audit_type(self):
        for key, value in AUDIT_TYPE_DICT.items():
            with self.subTest(key=key):
                general_information = {"audit_type": key}
                result = xform_audit_type(general_information)
                self.assertEqual(result["audit_type"], value)

    def test_invalid_audit_type(self):
        general_information = {"audit_type": "invalid_key"}
        with self.assertRaises(DataMigrationError):
            xform_audit_type(general_information)

    def test_missing_audit_type(self):
        general_information = {}
        with self.assertRaises(DataMigrationError):
            xform_audit_type(general_information)


class TestXformReplaceEmptyAuditorEmail(SimpleTestCase):
    def test_empty_auditor_email(self):
        """Test that an empty auditor_email is replaced with 'GSA_MIGRATION'"""
        input_data = {"auditor_email": ""}
        expected_output = {"auditor_email": settings.GSA_MIGRATION}
        self.assertEqual(xform_replace_empty_auditor_email(input_data), expected_output)

    def test_non_empty_auditor_email(self):
        """Test that a non-empty auditor_email remains unchanged"""
        input_data = {"auditor_email": "test@example.com"}
        expected_output = {"auditor_email": "test@example.com"}
        self.assertEqual(xform_replace_empty_auditor_email(input_data), expected_output)

    def test_missing_auditor_email(self):
        """Test that a missing auditor_email key is added and set to 'GSA_MIGRATION'"""
        input_data = {}
        expected_output = {"auditor_email": settings.GSA_MIGRATION}
        self.assertEqual(xform_replace_empty_auditor_email(input_data), expected_output)
