from unittest.mock import patch
from django.conf import settings
from django.test import SimpleTestCase

from .exception_utils import DataMigrationError
from .workbooklib.federal_awards import (
    is_valid_prefix,
    xform_populate_default_award_identification_values,
    xform_populate_default_loan_balance,
    xform_constructs_cluster_names,
    xform_populate_default_passthrough_amount,
    xform_populate_default_passthrough_values,
    xform_replace_invalid_extension,
    is_valid_extension,
)


class TestXformConstructsClusterNames(SimpleTestCase):
    class MockAudit:
        def __init__(self, cluster_name, state_cluster_name, other_cluster_name):
            self.CLUSTERNAME = cluster_name
            self.STATECLUSTERNAME = state_cluster_name
            self.OTHERCLUSTERNAME = other_cluster_name

    def test_empty_audits_list(self):
        """Test the function with an empty audits list."""
        result = xform_constructs_cluster_names([])
        self.assertEqual(result, ([], [], []))

    def test_empty_cluster_names(self):
        """Test the function with empty cluster names."""
        audits = [self.MockAudit("", "", "")]
        result = xform_constructs_cluster_names(audits)
        self.assertEqual(result, ([settings.GSA_MIGRATION], [""], [""]))

        audits.append(self.MockAudit("", "Some State Cluster", ""))
        result = xform_constructs_cluster_names(audits)
        result = tuple(sorted(sublist) for sublist in result)
        expected = (
            [settings.GSA_MIGRATION, settings.GSA_MIGRATION],
            ["", ""],
            ["", "Some State Cluster"],
        )
        expected = tuple(sorted(sublist) for sublist in expected)
        self.assertEqual(result, expected)

        audits.append(self.MockAudit("", "", "Some Other Cluster"))
        result = xform_constructs_cluster_names(audits)
        result = tuple(sorted(sublist) for sublist in result)
        expected = (
            [settings.GSA_MIGRATION, settings.GSA_MIGRATION, settings.GSA_MIGRATION],
            ["", "", "Some Other Cluster"],
            ["", "Some State Cluster", ""],
        )
        expected = tuple(sorted(sublist) for sublist in expected)
        self.assertEqual(
            result,
            expected,
        )

    def test_valid_cluster_name_combinations(self):
        """Test the function with valid cluster name combinations."""
        audits = [self.MockAudit("Normal Cluster", "", "")]
        result = xform_constructs_cluster_names(audits)
        self.assertEqual(result, (["Normal Cluster"], [""], [""]))

        audits.append(self.MockAudit("STATE CLUSTER", "Some State Cluster", ""))
        result = xform_constructs_cluster_names(audits)
        result = tuple(sorted(sublist) for sublist in result)
        expected = (
            ["Normal Cluster", "STATE CLUSTER"],
            ["", ""],
            ["", "Some State Cluster"],
        )
        expected = tuple(sorted(sublist) for sublist in expected)
        self.assertEqual(
            result,
            expected,
        )

        audits.append(
            self.MockAudit("OTHER CLUSTER NOT LISTED ABOVE", "", "Some Other Cluster")
        )
        result = xform_constructs_cluster_names(audits)
        result = tuple(sorted(sublist) for sublist in result)
        expected = (
            ["Normal Cluster", "STATE CLUSTER", "OTHER CLUSTER NOT LISTED ABOVE"],
            ["", "", "Some Other Cluster"],
            ["", "Some State Cluster", ""],
        )
        expected = tuple(sorted(sublist) for sublist in expected)
        self.assertEqual(
            result,
            expected,
        )

    def test_data_migration_error(self):
        """Test the function raises DataMigrationError when cluster name combination is invalid."""
        audits = [
            self.MockAudit("Cluster Name", "State Cluster Name", "Other Cluster Name")
        ]
        with self.assertRaises(DataMigrationError):
            xform_constructs_cluster_names(audits)

        audits = [self.MockAudit("Cluster Name", "State Cluster Name", "")]
        with self.assertRaises(DataMigrationError):
            xform_constructs_cluster_names(audits)

        audits = [self.MockAudit("Cluster Name", "", "Other Cluster Name")]
        with self.assertRaises(DataMigrationError):
            xform_constructs_cluster_names(audits)


class TestXformPopulateDefaultLoanBalance(SimpleTestCase):
    class MockAudit:
        def __init__(self, LOANS, LOANBALANCE):
            self.LOANS = LOANS
            self.LOANBALANCE = LOANBALANCE

    def test_loan_with_no_balance(self):
        """Test the function with a loan with no balance."""
        audits = [self.MockAudit(LOANS="Y", LOANBALANCE="")]
        expected = [settings.GSA_MIGRATION]
        self.assertEqual(xform_populate_default_loan_balance(audits), expected)

    def test_loan_with_balance(self):
        """Test the function with a loan with a balance."""
        audits = [self.MockAudit(LOANS="Y", LOANBALANCE="100")]
        expected = ["100"]
        self.assertEqual(xform_populate_default_loan_balance(audits), expected)

    def test_no_loan(self):
        """Test the function with no loan."""
        audits = [self.MockAudit(LOANS="N", LOANBALANCE="")]
        expected = [""]
        self.assertEqual(xform_populate_default_loan_balance(audits), expected)

    def test_unexpected_loan_balance(self):
        """Test the function raises DataMigrationError when loan balance is unexpected."""
        audits = [self.MockAudit(LOANS="N", LOANBALANCE="100")]
        with self.assertRaises(DataMigrationError):
            xform_populate_default_loan_balance(audits)


class TestXformPopulateDefaultAwardIdentificationValues(SimpleTestCase):
    class MockAudit:
        def __init__(self, CFDA, AWARDIDENTIFICATION):
            self.CFDA = CFDA
            self.AWARDIDENTIFICATION = AWARDIDENTIFICATION

    def test_cfda_with_u_no_identification(self):
        """Test the function with a CFDA with a U and no identification."""
        audits = [self.MockAudit(CFDA="123U", AWARDIDENTIFICATION="")]
        expected = [settings.GSA_MIGRATION]
        self.assertEqual(
            xform_populate_default_award_identification_values(audits), expected
        )

    def test_cfda_with_rd_no_identification(self):
        """Test the function with a CFDA with a RD and no identification."""
        audits = [self.MockAudit(CFDA="rd123", AWARDIDENTIFICATION="")]
        expected = [settings.GSA_MIGRATION]
        self.assertEqual(
            xform_populate_default_award_identification_values(audits), expected
        )

    def test_cfda_without_u_or_rd(self):
        """Test the function with a CFDA without a U or RD."""
        audits = [self.MockAudit(CFDA="12345", AWARDIDENTIFICATION="")]
        expected = [""]
        self.assertEqual(
            xform_populate_default_award_identification_values(audits), expected
        )

    def test_cfda_with_identification(self):
        """Test the function with a CFDA with an identification."""
        audits = [self.MockAudit(CFDA="U123", AWARDIDENTIFICATION="ABC")]
        expected = ["ABC"]
        self.assertEqual(
            xform_populate_default_award_identification_values(audits), expected
        )


class TestXformPopulateDefaultPassthroughValues(SimpleTestCase):
    class MockAudit:
        def __init__(self, DIRECT, DBKEY, AUDITYEAR, ELECAUDITSID):
            self.DIRECT = DIRECT
            self.DBKEY = DBKEY
            self.AUDITYEAR = AUDITYEAR
            self.ELECAUDITSID = ELECAUDITSID

    class MockPassthrough:
        def __init__(self, PASSTHROUGHNAME, PASSTHROUGHID):
            self.PASSTHROUGHNAME = PASSTHROUGHNAME
            self.PASSTHROUGHID = PASSTHROUGHID

    @patch("census_historical_migration.workbooklib.federal_awards._get_passthroughs")
    def test_direct_N_empty_name_and_id(self, mock_get_passthroughs):
        """Test the function with a direct N audit with empty name and id."""
        mock_get_passthroughs.return_value = ([""], [""])
        audits = [
            self.MockAudit(
                DIRECT="N", DBKEY="DBKEY2", AUDITYEAR="2022", ELECAUDITSID="1"
            )
        ]

        names, ids = xform_populate_default_passthrough_values(audits)

        self.assertEqual(names[0], settings.GSA_MIGRATION)
        self.assertEqual(ids[0], settings.GSA_MIGRATION)

    @patch("census_historical_migration.workbooklib.federal_awards._get_passthroughs")
    def test_direct_N_non_empty_name_and_id(self, mock_get_passthroughs):
        """Test the function with a direct N audit with non-empty name and id."""
        mock_get_passthroughs.return_value = (["Name1|Name2"], ["ID1|ID2"])
        audits = [
            self.MockAudit(
                DIRECT="N", DBKEY="DBKEY1", AUDITYEAR="2022", ELECAUDITSID="2"
            )
        ]

        names, ids = xform_populate_default_passthrough_values(audits)

        self.assertEqual(names[0], "Name1|Name2")
        self.assertEqual(ids[0], "ID1|ID2")

    @patch("census_historical_migration.workbooklib.federal_awards._get_passthroughs")
    def test_direct_Y_empty_name_and_id(self, mock_get_passthroughs):
        """Test the function with a direct Y audit with empty name and id."""
        mock_get_passthroughs.return_value = ([""], [""])
        audits = [
            self.MockAudit(
                DIRECT="Y", DBKEY="DBKEY1", AUDITYEAR="2022", ELECAUDITSID="3"
            )
        ]

        names, ids = xform_populate_default_passthrough_values(audits)

        self.assertEqual(names[0], "")
        self.assertEqual(ids[0], "")

    @patch("census_historical_migration.workbooklib.federal_awards._get_passthroughs")
    def test_direct_Y_non_empty_name_and_id(self, mock_get_passthroughs):
        """Test the function with a direct Y audit with non-empty name and id."""
        mock_get_passthroughs.return_value = (["Name"], ["ID"])
        audits = [
            self.MockAudit(
                DIRECT="Y", DBKEY="DBKEY1", AUDITYEAR="2022", ELECAUDITSID="4"
            )
        ]

        names, ids = xform_populate_default_passthrough_values(audits)

        self.assertEqual(names[0], "Name")
        self.assertEqual(ids[0], "ID")


class TestXformPopulateDefaultPassthroughAmount(SimpleTestCase):
    class MockAudit:
        def __init__(self, PASSTHROUGHAWARD, PASSTHROUGHAMOUNT):
            self.PASSTHROUGHAWARD = PASSTHROUGHAWARD
            self.PASSTHROUGHAMOUNT = PASSTHROUGHAMOUNT

    def test_passthrough_award_Y_non_empty_amount(self):
        """Test the function with a passthrough award Y audit with non-empty amount."""
        audits = [self.MockAudit(PASSTHROUGHAWARD="Y", PASSTHROUGHAMOUNT="100")]
        expected = ["100"]
        self.assertEqual(xform_populate_default_passthrough_amount(audits), expected)

    def test_passthrough_award_N_empty_amount(self):
        """Test the function with a passthrough award N audit with empty amount."""
        audits = [self.MockAudit(PASSTHROUGHAWARD="N", PASSTHROUGHAMOUNT="")]
        expected = [""]
        self.assertEqual(xform_populate_default_passthrough_amount(audits), expected)

    def test_passthrough_award_N_zero_amount(self):
        """Test the function with a passthrough award N audit with zero amount."""
        audits = [self.MockAudit(PASSTHROUGHAWARD="N", PASSTHROUGHAMOUNT="0")]
        expected = [""]
        self.assertEqual(xform_populate_default_passthrough_amount(audits), expected)

    def test_passthrough_award_N_unexpected_amount(self):
        """Test the function raises DataMigrationError when passthrough award N and amount is unexpected."""
        audits = [self.MockAudit(PASSTHROUGHAWARD="N", PASSTHROUGHAMOUNT="100")]
        with self.assertRaises(DataMigrationError):
            xform_populate_default_passthrough_amount(audits)

    def test_passthrough_award_Y_empty_amount(self):
        """Test for default value when passthrough award Y audit with empty amount."""
        audits = [self.MockAudit(PASSTHROUGHAWARD="Y", PASSTHROUGHAMOUNT="")]
        expected = [str(settings.GSA_MIGRATION_INT)]
        self.assertEqual(xform_populate_default_passthrough_amount(audits), expected)


class TestCFDAFunctions(SimpleTestCase):
    def test_is_valid_prefix(self):
        """Test the function with valid and invalid prefixes."""
        self.assertTrue(is_valid_prefix("01"))
        self.assertFalse(is_valid_prefix("ABC"))
        self.assertFalse(is_valid_prefix("123"))

    def test_is_valid_extension(self):
        """Test the function with valid and invalid extensions."""
        self.assertTrue(is_valid_extension("RD"))
        self.assertTrue(is_valid_extension("RD1"))
        self.assertTrue(is_valid_extension("123A"))
        self.assertTrue(is_valid_extension("U01"))
        # Invalid cases
        self.assertFalse(is_valid_extension("RDABC"))
        self.assertFalse(is_valid_extension("12345"))
        self.assertFalse(is_valid_extension("UA123"))

    def test_xform_replace_invalid_extension(self):
        class MockAudit:
            def __init__(self, prefix, ext):
                self.CFDA_PREFIX = prefix
                self.CFDA_EXT = ext

        # Valid prefix and extension
        audit = MockAudit("01", "RD1")
        result, _ = xform_replace_invalid_extension(audit)
        self.assertEqual(result, "01.RD1")

        # Invalid prefix
        audit = MockAudit("ABC", "RD1")
        with self.assertRaises(DataMigrationError):
            xform_replace_invalid_extension(audit)

        # Invalid extension
        audit = MockAudit("01", "ABC")
        result, _ = xform_replace_invalid_extension(audit)
        self.assertEqual(result, f"01.{settings.GSA_MIGRATION}")
