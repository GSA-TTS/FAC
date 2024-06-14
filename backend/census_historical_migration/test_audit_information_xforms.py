from unittest.mock import MagicMock, patch
from django.test import SimpleTestCase, TestCase

from .sac_general_lib.audit_information import (
    ace_audit_information,
    xform_build_sp_framework_gaap_results,
    xform_framework_basis,
    xform_sp_framework_required,
    xform_lowrisk,
)
from .exception_utils import DataMigrationError
from django.conf import settings


class TestXformBuildSpFrameworkGaapResults(SimpleTestCase):
    class MockAuditHeader:
        def __init__(
            self,
            DBKEY,
            TYPEREPORT_FS,
            SP_FRAMEWORK_REQUIRED,
            TYPEREPORT_SP_FRAMEWORK,
            SP_FRAMEWORK,
        ):
            self.DBKEY = DBKEY
            self.TYPEREPORT_FS = TYPEREPORT_FS
            self.SP_FRAMEWORK_REQUIRED = SP_FRAMEWORK_REQUIRED
            self.TYPEREPORT_SP_FRAMEWORK = TYPEREPORT_SP_FRAMEWORK
            self.SP_FRAMEWORK = SP_FRAMEWORK

    def _mock_audit_header(self):
        """Returns a mock audit header with all necessary fields."""
        return self.MockAuditHeader(
            DBKEY="123456789",
            TYPEREPORT_FS="UQADS",
            SP_FRAMEWORK_REQUIRED="Y",
            TYPEREPORT_SP_FRAMEWORK="UQAD",
            SP_FRAMEWORK="cash",
        )

    def test_normal_operation_with_all_opinions(self):
        """Test that the function returns the correct results when all opinions are present."""
        audit_header = self._mock_audit_header()
        result = xform_build_sp_framework_gaap_results(audit_header)
        self.assertIn("unmodified_opinion", result["gaap_results"])
        self.assertIn("qualified_opinion", result["gaap_results"])
        self.assertIn("adverse_opinion", result["gaap_results"])
        self.assertIn("disclaimer_of_opinion", result["gaap_results"])
        self.assertTrue(result["is_sp_framework_required"])
        self.assertIn("cash_basis", result["sp_framework_basis"])

    def test_missing_some_sp_framework_details(self):
        """Test that the function returns the correct results when some purpose framework details are missing."""
        audit_header = self._mock_audit_header()
        audit_header.TYPEREPORT_FS = "UQ"
        result = xform_build_sp_framework_gaap_results(audit_header)
        self.assertIn("unmodified_opinion", result["gaap_results"])
        self.assertIn("qualified_opinion", result["gaap_results"])
        self.assertNotIn("adverse_opinion", result["gaap_results"])
        self.assertNotIn("disclaimer_of_opinion", result["gaap_results"])
        self.assertNotIn("is_sp_framework_required", result)
        self.assertNotIn("sp_framework_basis", result)

    def test_missing_all_sp_framework_details(self):
        """Test that the function raises an exception when all special purpose framework details are missing."""
        audit_header = self._mock_audit_header()
        audit_header.TYPEREPORT_FS = ""
        with self.assertRaises(DataMigrationError):
            xform_build_sp_framework_gaap_results(audit_header)

    def test_incorrect_framework_basis(self):
        """Test that the function raises an exception when the special purpose framework basis is incorrect."""
        audit_header = self._mock_audit_header()
        audit_header.SP_FRAMEWORK = "incorrect_basis"
        with self.assertRaises(DataMigrationError):
            xform_build_sp_framework_gaap_results(audit_header)


class TestXformFrameworkBasis(SimpleTestCase):
    def test_valid_bases(self):
        """Test that the function returns the correct results for each basis in lower cases."""
        self.assertEqual(xform_framework_basis("cash"), "cash_basis")
        self.assertEqual(xform_framework_basis("contractual"), "contractual_basis")
        self.assertEqual(xform_framework_basis("regulatory"), "regulatory_basis")
        self.assertEqual(xform_framework_basis("tax"), "tax_basis")
        self.assertEqual(xform_framework_basis("other"), "other_basis")

    def test_basis_with_upper_cases(self):
        """Test that the function returns the correct results for each basis in upper cases."""
        self.assertEqual(xform_framework_basis("CASH"), "cash_basis")
        self.assertEqual(
            xform_framework_basis("OTHER"),
            "other_basis",
        )
        self.assertEqual(xform_framework_basis("REGULATORY"), "regulatory_basis")
        self.assertEqual(xform_framework_basis("TAX"), "tax_basis")
        self.assertEqual(
            xform_framework_basis("CONTRACTUAL"),
            "contractual_basis",
        )

    def test_invalid_basis(self):
        """Test that the function raises an exception when the basis is invalid."""
        with self.assertRaises(DataMigrationError):
            xform_framework_basis("equity")

    def test_empty_string(self):
        """Test that the function raises an exception when the basis is an empty string."""
        with self.assertRaises(DataMigrationError):
            xform_framework_basis("")

    def test_none_input(self):
        """Test that the function raises an exception when the basis is None."""
        with self.assertRaises(DataMigrationError):
            xform_framework_basis(None)

    def test_basis_with_multiple_spaces(self):
        """Test that the function returns the correct results when the basis has multiple spaces."""
        self.assertEqual(xform_framework_basis("  cash  "), "cash_basis")
        self.assertEqual(
            xform_framework_basis("  other  "),
            "other_basis",
        )
        with self.assertRaises(DataMigrationError):
            xform_framework_basis("  unknown  ")

    def test_basis_with_extra_words(self):
        """Test that the function raises an exception when the basis has extra words."""
        with self.assertRaises(DataMigrationError):
            xform_framework_basis("Something with cash basis")


class TestXformSpFrameworkRequired(SimpleTestCase):
    class MockAuditHeader:
        def __init__(
            self,
            DBKEY,
            TYPEREPORT_FS,
            SP_FRAMEWORK_REQUIRED,
        ):
            self.DBKEY = DBKEY
            self.TYPEREPORT_FS = TYPEREPORT_FS
            self.SP_FRAMEWORK_REQUIRED = SP_FRAMEWORK_REQUIRED

    def _mock_audit_header(self):
        """Returns a mock audit header with all necessary fields."""
        return self.MockAuditHeader(
            DBKEY="123456789",
            TYPEREPORT_FS="AS",
            SP_FRAMEWORK_REQUIRED="Y",
        )

    def test_sp_framework_required_Y(self):
        """Test that the function returns 'Y' for SP_FRAMEWORK_REQUIRED."""
        audit_header = self._mock_audit_header()
        xform_sp_framework_required(audit_header)
        self.assertEqual(audit_header.SP_FRAMEWORK_REQUIRED, "Y")

    def test_sp_framework_required_N(self):
        """Test that the function returns 'N' for SP_FRAMEWORK_REQUIRED."""
        audit_header = self._mock_audit_header()
        audit_header.SP_FRAMEWORK_REQUIRED = "N"
        xform_sp_framework_required(audit_header)
        self.assertEqual(audit_header.SP_FRAMEWORK_REQUIRED, "N")

    def test_sp_framework_required_blank(self):
        """Test that the function returns GSA_MIGRATION for SP_FRAMEWORK_REQUIRED."""
        audit_header = self._mock_audit_header()
        audit_header.SP_FRAMEWORK_REQUIRED = ""
        xform_sp_framework_required(audit_header)
        self.assertEqual(audit_header.SP_FRAMEWORK_REQUIRED, settings.GSA_MIGRATION)


class TestXformLowrisk(SimpleTestCase):
    class MockAuditHeader:
        def __init__(
            self,
            DBKEY,
            LOWRISK,
        ):
            self.DBKEY = DBKEY
            self.LOWRISK = LOWRISK

    def _mock_audit_header(self):
        """Returns a mock audit header with all necessary fields."""
        return self.MockAuditHeader(
            DBKEY="123456789",
            LOWRISK="Y",
        )

    def test_lowrisk_Y(self):
        """Test that the function returns 'Y' for LOWRISK."""
        audit_header = self._mock_audit_header()
        xform_lowrisk(audit_header)
        self.assertEqual(audit_header.LOWRISK, "Y")

    def test_lowrisk_N(self):
        """Test that the function returns 'N' for LOWRISK."""
        audit_header = self._mock_audit_header()
        audit_header.LOWRISK = "N"
        xform_lowrisk(audit_header)
        self.assertEqual(audit_header.LOWRISK, "N")

    def test_lowrisk_blank(self):
        """Test that the function returns GSA_MIGRATION for LOWRISK."""
        audit_header = self._mock_audit_header()
        audit_header.LOWRISK = ""
        xform_lowrisk(audit_header)
        self.assertEqual(audit_header.LOWRISK, settings.GSA_MIGRATION)


class TestAceAuditInformation(SimpleTestCase):

    def setUp(self):
        self.audit_header = MagicMock()
        self.audit_header.some_field = "test_value"

        self.default_values = {
            "dollar_threshold": settings.GSA_MIGRATION_INT,
            "gaap_results": [settings.GSA_MIGRATION],
            "is_going_concern_included": settings.GSA_MIGRATION,
            "is_internal_control_deficiency_disclosed": settings.GSA_MIGRATION,
            "is_internal_control_material_weakness_disclosed": settings.GSA_MIGRATION,
            "is_material_noncompliance_disclosed": settings.GSA_MIGRATION,
            "is_aicpa_audit_guide_included": settings.GSA_MIGRATION,
            "is_low_risk_auditee": settings.GSA_MIGRATION,
            "agencies": [settings.GSA_MIGRATION],
        }

    @patch(
        "census_historical_migration.sac_general_lib.audit_information.create_json_from_db_object"
    )
    def test_ace_audit_information_with_actual_values(self, mock_create_json):
        """Test that the function returns the correct values when all fields are present."""
        mock_create_json.return_value = {
            "dollar_threshold": 1000,
            "is_low_risk_auditee": True,
            "new_field": "new_value",
        }

        result = ace_audit_information(self.audit_header)

        expected_result = self.default_values.copy()
        expected_result.update(
            {
                "dollar_threshold": 1000,
                "is_low_risk_auditee": True,
                "new_field": "new_value",
            }
        )

        self.assertEqual(result, expected_result)

    @patch(
        "census_historical_migration.sac_general_lib.audit_information.create_json_from_db_object"
    )
    def test_ace_audit_information_with_default_values(self, mock_create_json):
        """Test that the function returns the correct values when all fields are missing."""
        mock_create_json.return_value = {}

        result = ace_audit_information(self.audit_header)

        expected_result = self.default_values

        self.assertEqual(result, expected_result)

    @patch(
        "census_historical_migration.sac_general_lib.audit_information.create_json_from_db_object"
    )
    def test_ace_audit_information_with_mixed_values(self, mock_create_json):
        """Test that the function returns the correct values when some fields are missing."""
        mock_create_json.return_value = {
            "dollar_threshold": None,
            "is_low_risk_auditee": True,
        }

        result = ace_audit_information(self.audit_header)

        expected_result = self.default_values.copy()
        expected_result.update({"is_low_risk_auditee": True})

        self.assertEqual(result, expected_result)
