from django.test import SimpleTestCase

from .sac_general_lib.audit_information import (
    xform_build_sp_framework_gaap_results,
    xform_framework_basis,
)
from .exception_utils import DataMigrationError


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
