from unittest.mock import patch
from django.conf import settings
from django.test import SimpleTestCase, TestCase

from .invalid_migration_tags import INVALID_MIGRATION_TAGS
from .invalid_record import InvalidRecord
from .transforms.xform_string_to_string import (
    string_to_string,
)
from .exception_utils import DataMigrationError
from .workbooklib.federal_awards import (
    is_valid_prefix,
    track_invalid_federal_program_total,
    track_invalid_number_of_audit_findings,
    xform_match_number_passthrough_names_ids,
    xform_missing_amount_expended,
    xform_missing_program_total,
    xform_missing_cluster_total_v2,
    xform_populate_default_award_identification_values,
    xform_populate_default_loan_balance,
    xform_constructs_cluster_names,
    xform_populate_default_passthrough_amount,
    xform_populate_default_passthrough_names_ids,
    xform_replace_invalid_direct_award_flag,
    xform_replace_invalid_extension,
    xform_program_name,
    xform_is_passthrough_award,
    xform_missing_major_program,
    is_valid_extension,
    xform_cluster_names,
    xform_replace_missing_prefix,
    xform_replace_required_values_with_gsa_migration_when_empty,
    xform_sanitize_additional_award_identification,
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

    def test_no_loan_with_zero_balance(self):
        """Test the function with no loan and zero balance."""
        audits = [self.MockAudit(LOANS="N", LOANBALANCE="0")]
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

        names, ids = xform_populate_default_passthrough_names_ids(audits)

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

        names, ids = xform_populate_default_passthrough_names_ids(audits)

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

        names, ids = xform_populate_default_passthrough_names_ids(audits)

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

        names, ids = xform_populate_default_passthrough_names_ids(audits)

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

    def test_passthrough_award_gsa_non_empty_amount(self):
        """Test the function with a passthrough award GSA_MIGRATION audit with non-empty amount."""
        audits = [
            self.MockAudit(
                PASSTHROUGHAWARD=settings.GSA_MIGRATION, PASSTHROUGHAMOUNT="100"
            )
        ]
        expected = ["100"]
        self.assertEqual(xform_populate_default_passthrough_amount(audits), expected)

    def test_passthrough_award_gsa_empty_amount(self):
        """Test the function with a passthrough award GSA_MIGRATIONN audit with empty amount."""
        audits = [
            self.MockAudit(
                PASSTHROUGHAWARD=settings.GSA_MIGRATION, PASSTHROUGHAMOUNT=""
            )
        ]
        expected = [""]
        self.assertEqual(xform_populate_default_passthrough_amount(audits), expected)

    def test_passthrough_award_gsa_zero_amount(self):
        """Test the function with a passthrough award GSA_MIGRATION audit with zero amount."""
        audits = [
            self.MockAudit(
                PASSTHROUGHAWARD=settings.GSA_MIGRATION, PASSTHROUGHAMOUNT="0"
            )
        ]
        expected = [""]
        self.assertEqual(xform_populate_default_passthrough_amount(audits), expected)


class TestXformIsPassthroughAward(SimpleTestCase):
    class MockAudit:
        def __init__(self, PASSTHROUGHAWARD, PASSTHROUGHAMOUNT):
            self.PASSTHROUGHAWARD = PASSTHROUGHAWARD
            self.PASSTHROUGHAMOUNT = PASSTHROUGHAMOUNT

    def test_passthrough_award_Y(self):
        """Test the function with a valid passthrough award."""
        audits = [self.MockAudit(PASSTHROUGHAWARD="Y", PASSTHROUGHAMOUNT="0")]
        expected = "Y"
        xform_is_passthrough_award(audits)
        self.assertEqual(audits[0].PASSTHROUGHAWARD, expected)

    def test_passthrough_award_empty_with_amount(self):
        """Test the function with an empty passthrough award and truthy amount."""
        audits = [self.MockAudit(PASSTHROUGHAWARD="", PASSTHROUGHAMOUNT="42")]
        expected = settings.GSA_MIGRATION
        xform_is_passthrough_award(audits)
        self.assertEqual(audits[0].PASSTHROUGHAWARD, expected)

    def test_passthrough_award_empty_with_no_amount(self):
        """Test the function with an empty passthrough award and 0 amount."""
        audits = [self.MockAudit(PASSTHROUGHAWARD="", PASSTHROUGHAMOUNT="0")]
        expected = settings.GSA_MIGRATION
        xform_is_passthrough_award(audits)
        self.assertEqual(audits[0].PASSTHROUGHAWARD, expected)

    def test_passthrough_award_empty_with_empty_amount(self):
        """Test the function with an empty passthrough award and empty amount."""
        audits = [self.MockAudit(PASSTHROUGHAWARD="", PASSTHROUGHAMOUNT="")]
        expected = settings.GSA_MIGRATION
        xform_is_passthrough_award(audits)
        self.assertEqual(audits[0].PASSTHROUGHAWARD, expected)


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


class TestXformMissingProgramTotal(SimpleTestCase):
    class AuditMock:
        def __init__(self, cfda_prefix, cfda_ext, amount, program_total=None):
            self.CFDA_PREFIX = cfda_prefix
            self.CFDA_EXT = cfda_ext
            self.AMOUNT = amount
            self.PROGRAMTOTAL = program_total

    def test_with_missing_program_total(self):
        """Test for missing program total"""
        audits = [
            self.AuditMock("10", "123", "100"),
            self.AuditMock("10", "123", "200"),
            self.AuditMock("20", "456", "300", "300"),
        ]
        expected_program_totals = {"10.123": "300", "20.456": "300"}

        xform_missing_program_total(audits)

        for audit in audits:
            cfda_key = f"{string_to_string(audit.CFDA_PREFIX)}.{string_to_string(audit.CFDA_EXT)}"
            self.assertEqual(audit.PROGRAMTOTAL, expected_program_totals[cfda_key])

    def test_preserve_existing_program_total(self):
        """Test for non missing program total"""
        audits = [
            self.AuditMock("10", "123", "100", "150"),
            self.AuditMock("10", "123", "200", "350"),
        ]
        # In this case, we expect the original PROGRAMTOTAL values to be preserved
        expected_program_totals = ["150", "350"]

        xform_missing_program_total(audits)

        for audit, expected in zip(audits, expected_program_totals):
            self.assertEqual(audit.PROGRAMTOTAL, expected)


class TestXformMissingClusterTotal(SimpleTestCase):
    class AuditMock:
        def __init__(
            self,
            amount,
            cluster_name,
            state_cluster_name="",
            other_cluster_name="",
            cluster_total="",
        ):
            self.AMOUNT = amount
            self.CLUSTERTOTAL = cluster_total
            self.CLUSTERNAME = cluster_name
            self.STATECLUSTERNAME = state_cluster_name
            self.OTHERCLUSTERNAME = other_cluster_name

    def test_xform_missing_cluster_total(self):
        """Test for missing cluster total"""
        audits = [
            self.AuditMock("100", "Cluster A"),
            self.AuditMock("150", "Cluster B"),
            self.AuditMock("150", "Cluster A", cluster_total="250"),
        ]
        cluster_names = ["Cluster A", "Cluster B", "Cluster A"]
        other_cluster_names = ["", "", ""]
        state_cluster_names = ["", "", ""]
        expected_totals = ["250", "150", "250"]

        xform_missing_cluster_total_v2(
            audits, cluster_names, other_cluster_names, state_cluster_names
        )

        for audit, expected in zip(audits, expected_totals):
            self.assertEqual(str(audit.CLUSTERTOTAL), expected)

    def test_xform_missing_cluster_total_with_state_cluster(self):
        """Test for missing state cluster total"""
        audits = [
            self.AuditMock("100", "Cluster A"),
            self.AuditMock(
                "150",
                settings.STATE_CLUSTER,
                state_cluster_name="State Cluster A",
                cluster_total="300",
            ),
            self.AuditMock("150", "Cluster A", cluster_total="250"),
            self.AuditMock(
                "150", settings.STATE_CLUSTER, state_cluster_name="State Cluster A"
            ),
        ]
        cluster_names = [
            "Cluster A",
            settings.STATE_CLUSTER,
            "Cluster A",
            settings.STATE_CLUSTER,
        ]
        other_cluster_names = ["", "", "", ""]
        state_cluster_names = ["", "State Cluster A", "", "State Cluster A"]
        expected_totals = ["250", "300", "250", "300"]

        xform_missing_cluster_total_v2(
            audits, cluster_names, other_cluster_names, state_cluster_names
        )

        for audit, expected in zip(audits, expected_totals):
            self.assertEqual(str(audit.CLUSTERTOTAL), expected)

    def test_xform_missing_cluster_total_with_other_cluster(self):
        """Test for missing other cluster total"""
        audits = [
            self.AuditMock("100", "Cluster A"),
            self.AuditMock(
                "150",
                settings.OTHER_CLUSTER,
                other_cluster_name="Other Cluster A",
                cluster_total="300",
            ),
            self.AuditMock("150", "Cluster A", cluster_total="250"),
            self.AuditMock(
                "150", settings.OTHER_CLUSTER, other_cluster_name="Other Cluster A"
            ),
        ]
        cluster_names = [
            "Cluster A",
            settings.OTHER_CLUSTER,
            "Cluster A",
            settings.OTHER_CLUSTER,
        ]
        state_cluster_names = ["", "", "", ""]
        other_cluster_names = ["", "Other Cluster A", "", "Other Cluster A"]
        expected_totals = ["250", "300", "250", "300"]

        xform_missing_cluster_total_v2(
            audits, cluster_names, other_cluster_names, state_cluster_names
        )

        for audit, expected in zip(audits, expected_totals):
            self.assertEqual(str(audit.CLUSTERTOTAL), expected)

    def test_xform_missing_cluster_total_invalid(self):
        """Test for incorrect cluster total"""
        audits = [
            self.AuditMock("150", "Cluster A", cluster_total="33"),
        ]
        cluster_names = ["Cluster A"]
        other_cluster_names = [""]
        state_cluster_names = [""]
        expected_totals = ["33"]

        InvalidRecord.reset()
        xform_missing_cluster_total_v2(
            audits, cluster_names, other_cluster_names, state_cluster_names
        )

        for audit, expected in zip(audits, expected_totals):
            self.assertEqual(str(audit.CLUSTERTOTAL), expected)

        self.assertEqual(
            InvalidRecord.fields["validations_to_skip"],
            ["cluster_total_is_correct"],
        )
        self.assertEqual(
            InvalidRecord.fields["federal_award"],
            [
                [
                    {
                        "census_data": [
                            {"column": "CLUSTERTOTAL", "value": 33},
                            {"column": "CLUSTERNAME", "value": "Cluster A"},
                            {"column": "STATECLUSTERNAME", "value": ""},
                            {"column": "OTHERCLUSTERNAME", "value": ""},
                        ],
                        "gsa_fac_data": {"field": "cluster_total", "value": 150},
                    }
                ]
            ],
        )


class TestXformMissingAmountExpended(SimpleTestCase):
    class AuditMock:
        def __init__(
            self,
            amount,
        ):
            self.AMOUNT = amount

    def setUp(self):
        self.audits = [
            self.AuditMock("100"),  # Normal case
            self.AuditMock(""),  # Empty string should default to '0'
            self.AuditMock(None),  # None should default to '0'
        ]

    def test_xform_missing_amount_expended(self):
        """Test for missing amount expended"""

        xform_missing_amount_expended(self.audits)

        expected_results = ["100", "0", "0"]
        actual_results = [audit.AMOUNT for audit in self.audits]

        self.assertEqual(actual_results, expected_results)


class TestXformMatchNumberPassthroughNamesIds(SimpleTestCase):
    def test_match_numbers_all_empty(self):
        """Test the function with all empty names and ids."""
        names = ["", "", ""]
        ids = ["", "", ""]
        expected_ids = ["", "", ""]

        transformed_names, transformed_ids = xform_match_number_passthrough_names_ids(
            names, ids
        )

        self.assertEqual(transformed_names, names)
        self.assertEqual(transformed_ids, expected_ids)

    def test_match_numbers_non_empty_names_empty_ids(self):
        """Test the function with non-empty names and empty ids."""
        names = ["name1|name2", "name3|name4"]
        ids = ["", ""]
        expected_ids = [
            f"{settings.GSA_MIGRATION}|{settings.GSA_MIGRATION}",
            f"{settings.GSA_MIGRATION}|{settings.GSA_MIGRATION}",
        ]

        transformed_names, transformed_ids = xform_match_number_passthrough_names_ids(
            names, ids
        )

        self.assertEqual(transformed_names, names)
        self.assertEqual(transformed_ids, expected_ids)

    def test_match_numbers_mixed_empty_and_non_empty(self):
        """Test the function with mixed empty and non-empty names and ids."""
        names = ["name1|name2|name3", "name4", "", "name5", ""]
        ids = ["id1", "", "id2", "id3|id4", ""]
        expected_ids = [
            f"id1|{settings.GSA_MIGRATION}|{settings.GSA_MIGRATION}",
            f"{settings.GSA_MIGRATION}",
            "id2",
            "id3|id4",
            "",
        ]

        expected_names = [
            "name1|name2|name3",
            "name4",
            f"{settings.GSA_MIGRATION}",
            f"name5|{settings.GSA_MIGRATION}",
            "",
        ]

        transformed_names, transformed_ids = xform_match_number_passthrough_names_ids(
            names, ids
        )

        self.assertEqual(transformed_names, expected_names)
        self.assertEqual(transformed_ids, expected_ids)


class TestXformMissingMajorProgram(SimpleTestCase):
    class AuditMock:
        def __init__(
            self,
            major_program,
            audit_type,
        ):
            self.MAJORPROGRAM = major_program
            self.TYPEREPORT_MP = audit_type

    def test_xform_normal_major_program(self):
        """Test for normal major program"""
        audits = [self.AuditMock("Y", "U")]

        xform_missing_major_program(audits)

        self.assertEqual(audits[0].MAJORPROGRAM, "Y")

    def test_xform_missing_major_program_with_audit_type(self):
        """Test for missing major program with audit type provided"""
        audits = [self.AuditMock("", "U")]

        xform_missing_major_program(audits)

        self.assertEqual(audits[0].MAJORPROGRAM, "Y")

    def test_xform_missing_major_program_without_audit_type(self):
        """Test for missing major program without audit type provided"""
        audits = [self.AuditMock("", "")]

        xform_missing_major_program(audits)

        self.assertEqual(audits[0].MAJORPROGRAM, "N")


class TestXformMissingProgramName(SimpleTestCase):
    class AuditMock:
        def __init__(self, program_name):
            self.FEDERALPROGRAMNAME = program_name

    def test_with_normal_program_name(self):
        """Test for missing program name"""
        audits = [self.AuditMock("Some fake name")]

        xform_program_name(audits)

        self.assertEqual(audits[0].FEDERALPROGRAMNAME, "Some fake name")

    def test_with_missing_program_name(self):
        """Test for missing program name"""
        audits = [self.AuditMock("")]

        xform_program_name(audits)

        self.assertEqual(audits[0].FEDERALPROGRAMNAME, settings.GSA_MIGRATION)


class TestXformClusterNames(SimpleTestCase):
    class MockAudit:
        def __init__(self, cluster_name):
            self.CLUSTERNAME = cluster_name

    def test_cluster_name_not_other_cluster(self):
        audits = []
        audits.append(self.MockAudit("STUDENT FINANCIAL ASSISTANCE"))
        audits.append(self.MockAudit("RESEARCH AND DEVELOPMENT"))
        result = xform_cluster_names(audits)
        for index in range(len(result)):
            self.assertEqual(result[index].CLUSTERNAME, audits[index].CLUSTERNAME)

    def test_cluster_name_other_cluster(self):
        audits = []
        audits.append(self.MockAudit("OTHER CLUSTER"))
        audits.append(self.MockAudit("OTHER CLUSTER"))
        result = xform_cluster_names(audits)
        for audit in result:
            self.assertEqual(audit.CLUSTERNAME, settings.OTHER_CLUSTER)


class TestXformReplaceInvalidDirectAwardFlag(SimpleTestCase):
    class MockAudit:
        def __init__(self, direct_flag):
            self.DIRECT = direct_flag

    def test_replace_invalid_direct_award_flag(self):
        audits = [self.MockAudit("Y"), self.MockAudit("N"), self.MockAudit("Y")]
        passthrough_names = [
            "some name",
            "some other name",
            "",
        ]

        results = xform_replace_invalid_direct_award_flag(audits, passthrough_names)
        # Expect first audit DIRECT flag to be replaced with default
        self.assertEqual(results[0], settings.GSA_MIGRATION)
        # Expect second audit DIRECT flag to remain unchanged
        self.assertEqual(results[1], "N")
        # Expect third audit DIRECT flag to remain unchanged
        self.assertEqual(results[2], "Y")


class TestXformSanitizeAdditionalAwardIdentification(SimpleTestCase):
    class MockAudit:
        def __init__(self, value):
            self.AWARDIDENTIFICATION = value

    def test_sanitize_valid(self):
        audits = [self.MockAudit('=""12345"'), self.MockAudit("text")]
        identifications = ['=""12345"', "text"]
        expected = ["12345", "text"]
        result = xform_sanitize_additional_award_identification(audits, identifications)
        self.assertEqual(result, expected)

    def test_empty_and_none_identifications(self):
        audits = [self.MockAudit(""), self.MockAudit(None), self.MockAudit('=""12345"')]
        identifications = ["", None, '=""12345"']
        expected = ["", None, "12345"]
        result = xform_sanitize_additional_award_identification(audits, identifications)
        self.assertEqual(result, expected)


class TestTrackInvalidFederalProgramTotal(SimpleTestCase):
    class MockAudit:
        def __init__(self, PROGRAMTOTAL, AMOUNT):
            self.PROGRAMTOTAL = PROGRAMTOTAL
            self.AMOUNT = AMOUNT

    def setUp(self):
        self.audits = [
            self.MockAudit(PROGRAMTOTAL="100", AMOUNT="50"),
            self.MockAudit(PROGRAMTOTAL="200", AMOUNT="200"),
            self.MockAudit(PROGRAMTOTAL="150", AMOUNT="100"),
        ]
        self.cfda_key_values = ["1234", "5678", "1234"]

        # Reset InvalidRecord before each test
        InvalidRecord.reset()

    def test_track_invalid_federal_program_total(self):
        """Test for invalid federal program total"""

        track_invalid_federal_program_total(self.audits, self.cfda_key_values)

        # Check the results in InvalidRecord
        self.assertEqual(len(InvalidRecord.fields["federal_award"]), 1)
        self.assertIn(
            "federal_program_total_is_correct",
            InvalidRecord.fields["validations_to_skip"],
        )
        self.assertIn(
            INVALID_MIGRATION_TAGS.INVALID_FEDERAL_PROGRAM_TOTAL,
            InvalidRecord.fields["invalid_migration_tag"],
        )

    def test_no_invalid_federal_program_total(self):
        # Adjust mock data for no invalid records
        self.audits = [
            self.MockAudit(PROGRAMTOTAL="150", AMOUNT="50"),
            self.MockAudit(PROGRAMTOTAL="200", AMOUNT="200"),
            self.MockAudit(PROGRAMTOTAL="150", AMOUNT="100"),
        ]

        track_invalid_federal_program_total(self.audits, self.cfda_key_values)

        # Check that no invalid records are added
        self.assertEqual(len(InvalidRecord.fields["federal_award"]), 0)
        self.assertNotIn(
            "federal_program_total_is_correct",
            InvalidRecord.fields["validations_to_skip"],
        )
        self.assertNotIn


class TestTrackInvalidNumberOfAuditFindings(TestCase):

    class MockAudit:
        def __init__(self, elec_audits_id, findings_count):
            self.ELECAUDITSID = elec_audits_id
            self.FINDINGSCOUNT = findings_count

    class MockFinding:
        def __init__(self, elec_audits_id):
            self.ELECAUDITSID = elec_audits_id

    class MockAuditHeader:
        def __init__(self, dbkey, audityear):
            self.DBKEY = dbkey
            self.AUDITYEAR = audityear

    def setUp(self):

        InvalidRecord.reset()

    @patch("census_historical_migration.workbooklib.federal_awards.get_findings")
    def test_track_invalid_number_of_audit_findings(self, mock_get_findings):
        """Test tracking for invalid number of audit findings"""
        # Mock the findings and audits data
        mock_findings = [
            self.MockFinding("audit1"),
            self.MockFinding("audit1"),
        ]

        mock_audits = [
            self.MockAudit("audit1", "2"),
            self.MockAudit("audit2", "1"),
        ]

        mock_audit_header = self.MockAuditHeader("some_dbkey", "2024")

        mock_get_findings.return_value = mock_findings

        track_invalid_number_of_audit_findings(mock_audits, mock_audit_header)
        mock_get_findings.assert_called_once_with("some_dbkey", "2024")
        # Check if the invalid records were appended correctly
        expected_invalid_records = [
            [
                {
                    "census_data": [
                        {"column": "ELECAUDITSID", "value": "audit1"},
                        {"column": "FINDINGSCOUNT", "value": "2"},
                    ],
                    "gsa_fac_data": {"field": "findings_count", "value": "2"},
                },
                {
                    "census_data": [
                        {"column": "ELECAUDITSID", "value": "audit2"},
                        {"column": "FINDINGSCOUNT", "value": "1"},
                    ],
                    "gsa_fac_data": {"field": "findings_count", "value": "0"},
                },
            ]
        ]

        for expected_record in expected_invalid_records:
            self.assertIn(expected_record, InvalidRecord.fields["federal_award"])

    @patch("census_historical_migration.workbooklib.federal_awards.get_findings")
    def test_no_tracking_with_valid_number_of_audit_findings(self, mock_get_findings):
        """Test no tracking for valid number of audit findings"""
        # Mock the findings and audits data
        mock_findings = [
            self.MockFinding("audit1"),
            self.MockFinding("audit1"),
        ]

        mock_audits = [
            self.MockAudit("audit1", "2"),
        ]

        mock_audit_header = self.MockAuditHeader("some_dbkey", "2024")
        mock_get_findings.return_value = mock_findings

        track_invalid_number_of_audit_findings(mock_audits, mock_audit_header)

        mock_get_findings.assert_called_once_with("some_dbkey", "2024")
        self.assertEqual(len(InvalidRecord.fields["federal_award"]), 0)


class TestXformMissingPrefix(SimpleTestCase):
    class MockAudit:

        def __init__(self, CFDA_PREFIX, CFDA):
            self.CFDA_PREFIX = CFDA_PREFIX
            self.CFDA = CFDA

    def test_for_no_missing_prefix(self):
        """Test for no missing prefix"""
        audits = [self.MockAudit("01", "01.123"), self.MockAudit("02", "02.456")]

        xform_replace_missing_prefix(audits)

        self.assertEqual(audits[0].CFDA_PREFIX, "01")
        self.assertEqual(audits[1].CFDA_PREFIX, "02")

    def test_for_missing_prefix(self):
        """Test for missing prefix"""
        audits = [self.MockAudit("", "01.123"), self.MockAudit("02", "02.456")]

        xform_replace_missing_prefix(audits)

        self.assertEqual(audits[0].CFDA_PREFIX, "01")
        self.assertEqual(audits[1].CFDA_PREFIX, "02")


class TestXformReplaceMissingFields(SimpleTestCase):

    class MockAudit:

        def __init__(
            self,
            LOANS,
            DIRECT,
        ):
            self.LOANS = LOANS
            self.DIRECT = DIRECT

    def test_replace_empty_fields(self):
        audits = [
            self.MockAudit(
                LOANS="",
                DIRECT="",
            ),
            self.MockAudit(
                LOANS="Present",
                DIRECT="Present",
            ),
        ]

        xform_replace_required_values_with_gsa_migration_when_empty(audits)

        self.assertEqual(audits[0].LOANS, settings.GSA_MIGRATION)
        self.assertEqual(audits[0].DIRECT, settings.GSA_MIGRATION)

        self.assertEqual(audits[1].LOANS, "Present")
        self.assertEqual(audits[1].DIRECT, "Present")
