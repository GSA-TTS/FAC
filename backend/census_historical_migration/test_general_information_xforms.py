from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
from unittest.mock import mock_open, patch
from django.conf import settings
from django.test import SimpleTestCase

from .sac_general_lib.general_information import (
    AUDIT_TYPE_DICT,
    PERIOD_DICT,
    is_uei_valid,
    xform_audit_period_covered,
    xform_audit_type,
    xform_auditee_fiscal_period_end,
    xform_auditee_fiscal_period_start,
    xform_country_v2,
    xform_entity_type,
    xform_replace_empty_auditee_contact_name,
    xform_replace_empty_auditee_contact_title,
    xform_replace_empty_auditor_email,
    xform_replace_empty_auditee_email,
    xform_replace_empty_or_invalid_auditee_uei_with_gsa_migration,
    xform_replace_empty_or_invalid_auditor_ein_with_gsa_migration,
    xform_replace_empty_or_invalid_auditee_ein_with_gsa_migration,
    xform_replace_empty_zips,
    xform_audit_period_other_months,
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
            self.CPASTREET1 = ""
            self.CPACITY = ""
            self.CPAZIPCODE = ""
            self.CPAFOREIGN = ""

    def setUp(self):
        self.general_information = {
            "auditor_country": "",
        }
        self.audit_header = self.MockAuditHeader("")

    def test_when_auditor_country_set_to_us(self):
        """Test that the function returns the correct results when the auditor country is set to US."""
        self.general_information["auditor_country"] = "US"
        result = xform_country_v2(self.general_information, self.audit_header)
        self.assertEqual(result["auditor_country"], "USA")

    def test_when_auditor_country_set_to_usa(self):
        """Test that the function returns the correct results when the auditor country is set to USA."""
        self.general_information["auditor_country"] = "USA"
        result = xform_country_v2(self.general_information, self.audit_header)
        self.assertEqual(result["auditor_country"], "USA")

    def test_when_auditor_country_set_to_empty_string_and_auditor_state_valid(self):
        """Test that the function returns the correct results when the auditor country is set to an empty string."""
        self.general_information["auditor_country"] = ""
        self.audit_header.CPASTATE = "MA"
        result = xform_country_v2(self.general_information, self.audit_header)
        self.assertEqual(result["auditor_country"], "USA")

    def test_when_auditor_country_set_to_empty_string_and_auditor_state_invalid(self):
        """Test that the function raises an exception when the auditor country is set to an empty string and the auditor state is invalid."""
        self.general_information["auditor_country"] = ""
        self.audit_header.CPASTATE = "XX"
        with self.assertRaises(DataMigrationError):
            xform_country_v2(self.general_information, self.audit_header)

    def test_when_auditor_country_set_to_non_us(self):
        """Test that the function returns the correct results when the auditor country is set to NON-US."""
        self.general_information["auditor_country"] = "NON-US"
        self.audit_header.CPAFOREIGN = "Some foreign address"
        result = xform_country_v2(self.general_information, self.audit_header)
        self.assertEqual(result["auditor_country"], "non-USA")
        self.assertEqual(
            result["auditor_international_address"], "Some foreign address"
        )

    def test_when_auditor_country_set_to_non_us_and_state_set(self):
        """Test that the function raises an exception when the auditor country is NON-US and the auditor state is set."""
        self.general_information["auditor_country"] = "NON-US"
        self.audit_header.CPASTATE = "MA"
        with self.assertRaises(DataMigrationError):
            xform_country_v2(self.general_information, self.audit_header)


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
        fiscal_end = datetime.strptime(
            self.general_information["auditee_fiscal_period_end"],
            "%m/%d/%Y %H:%M:%S",
        )
        expected_date = (
            fiscal_end - relativedelta(years=1) + timedelta(days=1)
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
            if value != "alternative-compliance-engagement":
                with self.subTest(key=key):
                    general_information = {"audit_type": key}
                    result = xform_audit_type(general_information)
                    self.assertEqual(result["audit_type"], value)

    def test_invalid_audit_type(self):
        general_information = {"audit_type": "invalid_key"}
        with self.assertRaises(DataMigrationError):
            xform_audit_type(general_information)

    def test_ace_audit_type(self):
        # audit type "alternative-compliance-engagement" is not supported at this time.
        general_information = {"audit_type": AUDIT_TYPE_DICT["A"]}
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


class TestXformReplaceEmptyAuditeeEmail(SimpleTestCase):
    def test_empty_auditee_email(self):
        """Test that an empty auditee_email is replaced with 'GSA_MIGRATION'"""
        input_data = {"auditee_email": ""}
        expected_output = {"auditee_email": settings.GSA_MIGRATION}
        self.assertEqual(xform_replace_empty_auditee_email(input_data), expected_output)

    def test_non_empty_auditee_email(self):
        """Test that a non-empty auditee_email remains unchanged"""
        input_data = {"auditee_email": "test@example.com"}
        expected_output = {"auditee_email": "test@example.com"}
        self.assertEqual(xform_replace_empty_auditee_email(input_data), expected_output)

    def test_missing_auditee_email(self):
        """Test that a missing auditee_email key is added and set to 'GSA_MIGRATION'"""
        input_data = {}
        expected_output = {"auditee_email": settings.GSA_MIGRATION}
        self.assertEqual(xform_replace_empty_auditee_email(input_data), expected_output)


class TestXformReplaceEmptyAuditeeContactName(SimpleTestCase):
    def test_empty_auditee_contact_name(self):
        """Test that an empty auditee_contact_name is replaced with 'GSA_MIGRATION'"""
        input_data = {"auditee_contact_name": ""}
        expected_output = {"auditee_contact_name": settings.GSA_MIGRATION}
        self.assertEqual(
            xform_replace_empty_auditee_contact_name(input_data), expected_output
        )

    def test_non_empty_auditee_contact_name(self):
        """Test that a non-empty auditee_contact_name remains unchanged"""
        input_data = {"auditee_contact_name": "test"}
        expected_output = {"auditee_contact_name": "test"}
        self.assertEqual(
            xform_replace_empty_auditee_contact_name(input_data), expected_output
        )

    def test_missing_auditee_contact_name(self):
        """Test that a missing auditee_contact_name key is added and set to 'GSA_MIGRATION'"""
        input_data = {}
        expected_output = {"auditee_contact_name": settings.GSA_MIGRATION}
        self.assertEqual(
            xform_replace_empty_auditee_contact_name(input_data), expected_output
        )


class TestXformReplaceEmptyAuditeeContactTitle(SimpleTestCase):
    def test_empty_auditee_contact_title(self):
        """Test that an empty auditee_contact_title is replaced with 'GSA_MIGRATION'"""
        input_data = {"auditee_contact_title": ""}
        expected_output = {"auditee_contact_title": settings.GSA_MIGRATION}
        self.assertEqual(
            xform_replace_empty_auditee_contact_title(input_data), expected_output
        )

    def test_non_empty_auditee_contact_title(self):
        """Test that a non-empty auditee_contact_title remains unchanged"""
        input_data = {"auditee_contact_title": "test"}
        expected_output = {"auditee_contact_title": "test"}
        self.assertEqual(
            xform_replace_empty_auditee_contact_title(input_data), expected_output
        )

    def test_missing_auditee_contact_title(self):
        """Test that a missing auditee_contact_title key is added and set to 'GSA_MIGRATION'"""
        input_data = {}
        expected_output = {"auditee_contact_title": settings.GSA_MIGRATION}
        self.assertEqual(
            xform_replace_empty_auditee_contact_title(input_data), expected_output
        )


class TestXformReplaceEmptyOrInvalidUEIs(SimpleTestCase):
    class MockAuditHeader:
        def __init__(self, UEI):
            self.UEI = UEI

    def setUp(self):
        self.audit_header = self.MockAuditHeader("")
        self.valid_uei = "ZQGGHJH74DW7"
        self.invalid_uei = "123"
        self.uei_schema = {
            "oneOf": [
                {
                    "allOf": [
                        {"maxLength": 12, "minLength": 12},
                        {"pattern": "^[A-HJ-NP-Z1-9][A-HJ-NP-Z0-9]+$"},
                        {
                            "pattern": "^(?![A-HJ-NP-Z1-9]+[A-HJ-NP-Z0-9]*?[0-9]{9})[A-HJ-NP-Z0-9]*$"
                        },
                        {"pattern": "^(?![0-9]{9})"},
                    ],
                    "type": "string",
                },
                {"const": "GSA_MIGRATION", "type": "string"},
            ]
        }

    def test_auditee_uei_valid(self):
        """Test that valid auditee EIN is not replaced."""
        self.audit_header.UEI = "ZQGGHJH74DW7"
        result = xform_replace_empty_or_invalid_auditee_uei_with_gsa_migration(
            self.audit_header
        )
        print(result)
        self.assertEqual(result.UEI, "ZQGGHJH74DW7")

    def test_auditee_uei_invalid_replaced(self):
        """Test that invalid auditee UEI is replaced."""
        self.audit_header.UEI = "invalid_uei"
        with patch(
            "census_historical_migration.sac_general_lib.general_information.track_transformations"
        ) as mock_track:
            result = xform_replace_empty_or_invalid_auditee_uei_with_gsa_migration(
                self.audit_header
            )
            mock_track.assert_called_once_with(
                "UEI",
                "invalid_uei",
                "auditee_uei",
                settings.GSA_MIGRATION,
                "xform_replace_empty_or_invalid_auditee_uei_with_gsa_migration",
            )
            self.assertEqual(result.UEI, settings.GSA_MIGRATION)

    def test_auditee_uei_empty_replaced(self):
        """Test that empty auditee UEI is replaced."""
        self.audit_header.UEI = "auditee_uei"
        with patch(
            "census_historical_migration.sac_general_lib.general_information.track_transformations"
        ) as mock_track:
            result = xform_replace_empty_or_invalid_auditee_uei_with_gsa_migration(
                self.audit_header
            )
            mock_track.assert_called_once()
            self.assertEqual(result.UEI, settings.GSA_MIGRATION)

    @patch("builtins.open", side_effect=FileNotFoundError)
    @patch(
        "census_historical_migration.sac_general_lib.general_information.settings.OUTPUT_BASE_DIR",
        "some/dir",
    )
    def test_missing_schema_file(self, mock_open):
        with self.assertRaises(DataMigrationError) as context:
            is_uei_valid(self.valid_uei)
        self.assertIn(
            "UeiSchema.json file not found in some/dir", str(context.exception)
        )

    @patch("builtins.open", new_callable=mock_open, read_data="invalid json")
    @patch(
        "json.load",
        side_effect=json.decoder.JSONDecodeError(
            "Expecting value", "line 1 column 1 (char 0)", 0
        ),
    )
    @patch(
        "census_historical_migration.sac_general_lib.general_information.settings.OUTPUT_BASE_DIR",
        "some/dir",
    )
    def test_invalid_json_schema_file(self, mock_json_load, mock_open):
        with self.assertRaises(DataMigrationError) as context:
            is_uei_valid(self.valid_uei)
        self.assertIn(
            "UeiSchema.json file contains invalid JSON", str(context.exception)
        )


class TestXformReplaceEmptyOrInvalidEins(SimpleTestCase):
    def test_auditor_ein_valid(self):
        """Test that valid auditor EIN is not replaced."""
        info = {"auditor_ein": "123456789"}
        result = xform_replace_empty_or_invalid_auditor_ein_with_gsa_migration(info)
        self.assertEqual(result["auditor_ein"], "123456789")

    def test_auditor_ein_invalid_replaced(self):
        """Test that invalid auditor EIN is replaced."""
        info = {"auditor_ein": "invalid_ein"}
        with patch(
            "census_historical_migration.sac_general_lib.general_information.track_transformations"
        ) as mock_track:
            result = xform_replace_empty_or_invalid_auditor_ein_with_gsa_migration(info)
            mock_track.assert_called_once_with(
                "AUDITOR_EIN",
                "invalid_ein",
                "auditor_ein",
                settings.GSA_MIGRATION,
                "xform_replace_empty_or_invalid_auditor_ein_with_gsa_migration",
            )
            self.assertEqual(result["auditor_ein"], settings.GSA_MIGRATION)

    def test_auditor_ein_empty_replaced(self):
        """Test that empty auditor EIN is replaced."""
        info = {"auditor_ein": ""}
        with patch(
            "census_historical_migration.sac_general_lib.general_information.track_transformations"
        ) as mock_track:
            result = xform_replace_empty_or_invalid_auditor_ein_with_gsa_migration(info)
            mock_track.assert_called_once()
            self.assertEqual(result["auditor_ein"], settings.GSA_MIGRATION)

    def test_auditee_ein_valid(self):
        """Test that valid auditee EIN is not replaced."""
        info = {"ein": "123456789"}
        result = xform_replace_empty_or_invalid_auditee_ein_with_gsa_migration(info)
        self.assertEqual(result["ein"], "123456789")

    def test_auditee_ein_invalid_replaced(self):
        """Test that invalid auditee EIN is replaced."""
        info = {"ein": "invalid_ein"}
        with patch(
            "census_historical_migration.sac_general_lib.general_information.track_transformations"
        ) as mock_track:
            result = xform_replace_empty_or_invalid_auditee_ein_with_gsa_migration(info)
            mock_track.assert_called_once_with(
                "EIN",
                "invalid_ein",
                "auditee_ein",
                settings.GSA_MIGRATION,
                "xform_replace_empty_or_invalid_auditee_ein_with_gsa_migration",
            )
            self.assertEqual(result["ein"], settings.GSA_MIGRATION)

    def test_auditee_ein_empty_replaced(self):
        """Test that empty auditee EIN is replaced."""
        info = {"ein": ""}
        with patch(
            "census_historical_migration.sac_general_lib.general_information.track_transformations"
        ) as mock_track:
            result = xform_replace_empty_or_invalid_auditee_ein_with_gsa_migration(info)
            mock_track.assert_called_once()
            self.assertEqual(result["ein"], settings.GSA_MIGRATION)


class TestXformReplaceEmptyAuditorZip(SimpleTestCase):
    def test_empty_auditor_zip(self):
        """Test that an empty US auditor_zip and auditee_zip are replaced with 'GSA_MIGRATION'"""
        input_data = {
            "auditee_zip": "",
            "auditor_country": "USA",
            "auditor_zip": "",
        }
        expected_output = {
            "auditee_zip": settings.GSA_MIGRATION,
            "auditor_country": "USA",
            "auditor_zip": settings.GSA_MIGRATION,
        }
        self.assertEqual(xform_replace_empty_zips(input_data), expected_output)

    def test_empty_non_us_auditor_zip(self):
        """Test that an empty non-US auditor_zip is not replaced with 'GSA_MIGRATION'"""
        input_data = {
            "auditee_zip": "",
            "auditor_country": "non-USA",
            "auditor_zip": "",
        }
        expected_output = {
            "auditee_zip": settings.GSA_MIGRATION,
            "auditor_country": "non-USA",
            "auditor_zip": "",
        }
        self.assertEqual(xform_replace_empty_zips(input_data), expected_output)

    def test_non_empty_auditor_zip(self):
        """Test that a non-empty US auditor_zip and auditee_zip remain unchanged"""
        input_data = {
            "auditee_zip": "10108",
            "auditor_country": "USA",
            "auditor_zip": "12345",
        }
        self.assertEqual(xform_replace_empty_zips(input_data), input_data)


class TestXformAuditPeriodOtherMonths(SimpleTestCase):
    class MockAuditHeader:
        def __init__(self, PERIODCOVERED, NUMBERMONTHS):
            self.PERIODCOVERED = PERIODCOVERED
            self.NUMBERMONTHS = NUMBERMONTHS

    def setUp(self):
        self.audit_header = self.MockAuditHeader("", "")

    def test_periodcovered_other_zfill(self):
        """Test that audit_period_other_months is set to NUMBERMONTHS with padded zeroes"""
        self.audit_header.PERIODCOVERED = "O"
        self.audit_header.NUMBERMONTHS = "6"
        general_information = {
            "audit_period_other_months": "",
        }
        expected_output = {
            "audit_period_other_months": "06",
        }
        xform_audit_period_other_months(general_information, self.audit_header)
        self.assertEqual(
            general_information,
            expected_output,
        )

    def test_periodcovered_other_no_zfill(self):
        """Test that audit_period_other_months is set to NUMBERMONTHS without padded zeroes"""
        self.audit_header.PERIODCOVERED = "O"
        self.audit_header.NUMBERMONTHS = "14"
        general_information = {
            "audit_period_other_months": "",
        }
        expected_output = {
            "audit_period_other_months": "14",
        }
        xform_audit_period_other_months(general_information, self.audit_header)
        self.assertEqual(
            general_information,
            expected_output,
        )

    def test_periodcovered_not_other(self):
        """Test that audit_period_other_months is not set"""
        self.audit_header.PERIODCOVERED = "A"
        self.audit_header.NUMBERMONTHS = "10"
        general_information = {
            "audit_period_other_months": "",
        }
        expected_output = {
            "audit_period_other_months": "",
        }
        xform_audit_period_other_months(general_information, self.audit_header)
        self.assertEqual(
            general_information,
            expected_output,
        )
