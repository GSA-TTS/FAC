from django.conf import settings
from django.test import SimpleTestCase

from .exception_utils import DataMigrationError
from .workbooklib.notes_to_sefa import (
    xform_is_minimis_rate_used,
    xform_missing_note_title_and_content,
    xform_missing_notes_records_v2,
    xform_rate_content,
    xform_policies_content,
    xform_sanitize_policies_content,
)


class TestXformIsMinimisRateUsed(SimpleTestCase):
    def test_rate_used(self):
        """Test that the function returns 'Y' when the rate is used."""
        self.assertEqual(
            xform_is_minimis_rate_used("The auditee used the de minimis cost rate."),
            "Y",
        )

        self.assertEqual(
            xform_is_minimis_rate_used(
                "The School has elected to use the 10-percent de minimis indirect cost rate as allowed under the Uniform Guidance."
            ),
            "Y",
        )
        self.assertEqual(
            xform_is_minimis_rate_used(
                "They have used the de minimis rate for this project."
            ),
            "Y",
        )
        self.assertEqual(
            xform_is_minimis_rate_used(
                "The auditee organization elected to use the de minimis rate."
            ),
            "Y",
        )
        self.assertEqual(
            xform_is_minimis_rate_used(
                "The de minimis rate is used and is allowed under our policy."
            ),
            "Y",
        )
        self.assertEqual(
            xform_is_minimis_rate_used("The Organization utilizes the 10% de minimis"),
            "Y",
        )

    def test_rate_not_used(self):
        """Test that the function returns 'N' when the rate is not used."""
        self.assertEqual(
            xform_is_minimis_rate_used(
                "The auditee did not use the de minimis cost rate."
            ),
            "N",
        )
        self.assertEqual(
            xform_is_minimis_rate_used(
                "The Board has elected not to use the 10 percent de minimus indirect cost as allowed under the Uniform Guidance."
            ),
            "N",
        )
        self.assertEqual(
            xform_is_minimis_rate_used(
                "The organization did not use the de minimis rate."
            ),
            "N",
        )
        self.assertEqual(
            xform_is_minimis_rate_used(
                "It was decided not to use the de minimis rate in this case."
            ),
            "N",
        )
        self.assertEqual(
            xform_is_minimis_rate_used(
                "The institution has elected not to use the de minimis rate."
            ),
            "N",
        )
        self.assertEqual(
            xform_is_minimis_rate_used(
                "There are no additional indirect costs allocated to the Corporation."
            ),
            "N",
        )
        self.assertEqual(
            xform_is_minimis_rate_used(
                "The Project has decided not to utilize the ten percent de minimis"
            ),
            "N",
        )
        self.assertEqual(
            xform_is_minimis_rate_used("The Symphony did not utilize a 10%"),
            "N",
        )
        self.assertEqual(
            xform_is_minimis_rate_used("10% de minimis rate option was not utilized"),
            "N",
        )
        self.assertEqual(
            xform_is_minimis_rate_used("Did not make this election"),
            "N",
        )
        self.assertEqual(
            xform_is_minimis_rate_used("Has not made an election"),
            "N",
        )
        self.assertEqual(
            xform_is_minimis_rate_used("No election has been made"),
            "N",
        )
        self.assertEqual(
            xform_is_minimis_rate_used(
                "IntraHealth negotiates and utilizes an indirect cost rate with the federal government and therefore does not utilize the 10% de minimis cost rate option under Uniform Guidance."
            ),
            "N",
        )

    def test_rate_with_multiple_spaces(self):
        """Test that the function returns the correct results when the rate is used and there are multiple spaces between words."""
        self.assertEqual(
            xform_is_minimis_rate_used(
                "We  have  elected  to  use  the  de  minimis  rate."
            ),
            "Y",
        )
        self.assertEqual(
            xform_is_minimis_rate_used(
                "The  organization  did  not  use  the  de  minimis  rate."
            ),
            "N",
        )

    def test_ambiguous_or_unclear_raises_exception(self):
        """Test that the function raises an exception when rate usage is ambiguous or unclear."""
        with self.assertRaises(DataMigrationError):
            xform_is_minimis_rate_used(
                "The information regarding the de minimis rate is not clear."
            )

        with self.assertRaises(DataMigrationError):
            xform_is_minimis_rate_used(
                "It is unknown whether the de minimis rate was applied."
            )

    def test_empty_string(self):
        """Test that the function returns GSA MIGRATION keyword when the input is an empty string."""
        self.assertEqual(xform_is_minimis_rate_used(""), settings.GSA_MIGRATION)


class TestXformMissingNoteTitleAndContent(SimpleTestCase):
    class MockNote:
        def __init__(
            self,
            TITLE,
            CONTENT,
            TYPE_ID,
        ):
            self.TITLE = TITLE
            self.CONTENT = CONTENT
            self.TYPE_ID = TYPE_ID

    def _mock_notes_no_title(self):
        notes = []
        notes.append(
            self.MockNote(
                TITLE="",
                CONTENT="SUPPORTIVE HOUSING FOR THE ELDERLY (14.157) - Balances outstanding at the end of the audit period were 3356.",
                TYPE_ID=3,
            )
        )
        notes.append(
            self.MockNote(
                TITLE="",
                CONTENT="MORTGAGE INSURANCE FOR THE PURCHASE OR REFINANCING OF EXISTING MULTIFAMILY HOUSING PROJECTS (14.155) - Balances outstanding at the end of the audit period were 4040.",
                TYPE_ID=3,
            )
        )
        return notes

    def _mock_notes_no_content(self):
        notes = []
        notes.append(
            self.MockNote(
                TITLE="Loan/loan guarantee outstanding balances",
                CONTENT="",
                TYPE_ID=3,
            )
        )
        notes.append(
            self.MockNote(
                TITLE="Federally Funded Insured Mortgages and Capital Advances",
                CONTENT="",
                TYPE_ID=3,
            )
        )
        return notes

    def _mock_notes_with_title_content(self):
        notes = []
        notes.append(
            self.MockNote(
                TITLE="Loan/loan guarantee outstanding balances",
                CONTENT="SUPPORTIVE HOUSING FOR THE ELDERLY (14.157) - Balances outstanding at the end of the audit period were 4000.",
                TYPE_ID=3,
            )
        )
        notes.append(
            self.MockNote(
                TITLE="Federally Funded Insured Mortgages and Capital Advances",
                CONTENT="MORTGAGE INSURANCE FOR THE PURCHASE OR REFINANCING OF EXISTING MULTIFAMILY HOUSING PROJECTS (14.155) - Balances outstanding at the end of the audit period were 5000.",
                TYPE_ID=3,
            )
        )
        return notes

    def test_note_w_no_title(self):
        notes = self._mock_notes_no_title()
        result = xform_missing_note_title_and_content(notes)
        for note in result:
            self.assertIn(settings.GSA_MIGRATION, note.TITLE)
            self.assertNotIn(settings.GSA_MIGRATION, note.CONTENT)

    def test_note_w_no_content(self):
        notes = self._mock_notes_no_content()
        result = xform_missing_note_title_and_content(notes)
        for note in result:
            self.assertNotIn(settings.GSA_MIGRATION, note.TITLE)
            self.assertIn(settings.GSA_MIGRATION, note.CONTENT)

    def test_note_with_title_content(self):
        notes = self._mock_notes_with_title_content()
        result = xform_missing_note_title_and_content(notes)
        for note in result:
            self.assertNotIn(settings.GSA_MIGRATION, note.TITLE)
            self.assertNotIn(settings.GSA_MIGRATION, note.CONTENT)


class TestXformMissingNotesRecordsV2(SimpleTestCase):
    class MockAuditHeader:
        def __init__(
            self,
            DBKEY,
            AUDITYEAR,
        ):
            self.DBKEY = DBKEY
            self.AUDITYEAR = AUDITYEAR

    class MockNote:
        def __init__(
            self,
            TITLE,
            CONTENT,
            TYPE_ID,
            DBKEY,
            AUDITYEAR,
        ):
            self.TITLE = TITLE
            self.CONTENT = CONTENT
            self.TYPE_ID = TYPE_ID
            self.DBKEY = DBKEY
            self.AUDITYEAR = AUDITYEAR

    def _mock_notes_valid_year_policies_no_rate(self):
        notes = []
        notes.append(
            self.MockNote(
                TITLE="Significant Accounting Policies Used in Preparing the SEFA",
                CONTENT="Expenditures reported on the Schedule are reported on the accrual basis of accounting.  Such expenditures are recognized following the cost principles contained in the Uniform Guidance, wherein certain types of expenditures are not allowable or are limited as to reimbursement.",
                TYPE_ID=1,
                DBKEY="123456789",
                AUDITYEAR="2022",
            )
        )
        audit_header = self.MockAuditHeader(
            DBKEY="123456789",
            AUDITYEAR="2022",
        )
        return notes, audit_header

    def _mock_notes_valid_year_rate_no_policies(self):
        notes = []
        notes.append(
            self.MockNote(
                TITLE="10% De Minimis Cost Rate",
                CONTENT="The auditee did not elect to use the de minimis cost rate.",
                TYPE_ID=2,
                DBKEY="223456789",
                AUDITYEAR="2021",
            )
        )
        audit_header = self.MockAuditHeader(
            DBKEY="223456789",
            AUDITYEAR="2021",
        )
        return notes, audit_header

    def _mock_notes_valid_year_no_rate_no_policies(self):
        notes = []
        audit_header = self.MockAuditHeader(
            DBKEY="223456788",
            AUDITYEAR="2020",
        )
        return notes, audit_header

    def _mock_notes_valid_year_rate_policies(self):
        notes = []
        notes.append(
            self.MockNote(
                TITLE="10% De Minimis Cost Rate",
                CONTENT="The auditee did not elect to use the de minimis cost rate.",
                TYPE_ID=2,
                DBKEY="123456788",
                AUDITYEAR="2018",
            )
        )
        notes.append(
            self.MockNote(
                TITLE="Significant Accounting Policies Used in Preparing the SEFA",
                CONTENT="Expenditures reported on the Schedule are reported on the accrual basis of accounting.  Such expenditures are recognized following the cost principles contained in the Uniform Guidance, wherein certain types of expenditures are not allowable or are limited as to reimbursement.",
                TYPE_ID=1,
                DBKEY="123456788",
                AUDITYEAR="2018",
            )
        )
        audit_header = self.MockAuditHeader(
            DBKEY="123456788",
            AUDITYEAR="2018",
        )
        return notes, audit_header

    def _mock_notes_invalid_year_policies_no_rate(self):
        notes = []
        notes.append(
            self.MockNote(
                TITLE="Significant Accounting Policies Used in Preparing the SEFA",
                CONTENT="Expenditures reported on the Schedule are reported on the accrual basis of accounting.  Such expenditures are recognized following the cost principles contained in the Uniform Guidance, wherein certain types of expenditures are not allowable or are limited as to reimbursement.",
                TYPE_ID=1,
                DBKEY="124456788",
                AUDITYEAR="2015",
            )
        )
        audit_header = self.MockAuditHeader(
            DBKEY="124456788",
            AUDITYEAR="2015",
        )
        return notes, audit_header

    def _mock_notes_invalid_year_rate_no_policies(self):
        notes = []
        notes.append(
            self.MockNote(
                TITLE="10% De Minimis Cost Rate",
                CONTENT="The auditee did not elect to use the de minimis cost rate.",
                TYPE_ID=2,
                DBKEY="124456789",
                AUDITYEAR="2014",
            )
        )
        audit_header = self.MockAuditHeader(
            DBKEY="124456789",
            AUDITYEAR="2014",
        )
        return notes, audit_header

    def _mock_notes_invalid_year_no_rate_no_policies(self):
        notes = []
        audit_header = self.MockAuditHeader(
            DBKEY="134456788",
            AUDITYEAR="2013",
        )
        return notes, audit_header

    def _mock_notes_invalid_year_rate_policies(self):
        notes = []
        notes.append(
            self.MockNote(
                TITLE="10% De Minimis Cost Rate",
                CONTENT="The auditee did not elect to use the de minimis cost rate.",
                TYPE_ID=2,
                DBKEY="124466788",
                AUDITYEAR="1800",
            )
        )
        notes.append(
            self.MockNote(
                TITLE="Significant Accounting Policies Used in Preparing the SEFA",
                CONTENT="Expenditures reported on the Schedule are reported on the accrual basis of accounting.  Such expenditures are recognized following the cost principles contained in the Uniform Guidance, wherein certain types of expenditures are not allowable or are limited as to reimbursement.",
                TYPE_ID=1,
                DBKEY="124466788",
                AUDITYEAR="1800",
            )
        )
        audit_header = self.MockAuditHeader(
            DBKEY="124466788",
            AUDITYEAR="1800",
        )
        return notes, audit_header

    def test_xform_missing_notes_records_v2_with_valid_year_policies_no_rate(self):
        notes, audit_header = self._mock_notes_valid_year_policies_no_rate()
        policies_content = list(filter(lambda note: note.TYPE_ID == 1, notes))[
            0
        ].CONTENT
        rate_content = ""
        result_policies_content, result_rate_content = xform_missing_notes_records_v2(
            audit_header, policies_content, rate_content
        )
        self.assertEqual(policies_content, result_policies_content)
        self.assertEqual(rate_content, result_rate_content)

    def test_xform_missing_notes_records_v2_with_valid_year_rate_no_policies(self):
        notes, audit_header = self._mock_notes_valid_year_rate_no_policies()
        policies_content = ""
        rate_content = list(filter(lambda note: note.TYPE_ID == 2, notes))[0].CONTENT
        result_policies_content, result_rate_content = xform_missing_notes_records_v2(
            audit_header, policies_content, rate_content
        )
        self.assertEqual(rate_content, result_rate_content)
        self.assertEqual(policies_content, result_policies_content)

    def test_xform_missing_notes_records_v2_with_valid_year_no_rate_no_policies(self):
        notes, audit_header = self._mock_notes_valid_year_no_rate_no_policies()
        policies_content = ""
        rate_content = ""
        result_policies_content, result_rate_content = xform_missing_notes_records_v2(
            audit_header, policies_content, rate_content
        )
        self.assertEqual(settings.GSA_MIGRATION, result_policies_content)
        self.assertEqual(settings.GSA_MIGRATION, result_rate_content)

    def test_xform_missing_notes_records_v2_with_valid_year_rate_policies(self):
        notes, audit_header = self._mock_notes_valid_year_rate_policies()
        policies_content = list(filter(lambda note: note.TYPE_ID == 1, notes))[
            0
        ].CONTENT
        rate_content = list(filter(lambda note: note.TYPE_ID == 2, notes))[0].CONTENT
        result_policies_content, result_rate_content = xform_missing_notes_records_v2(
            audit_header, policies_content, rate_content
        )
        self.assertEqual(policies_content, result_policies_content)
        self.assertEqual(rate_content, result_rate_content)

    def test_xform_missing_notes_records_v2_with_invalid_year_policies_no_rate(self):
        notes, audit_header = self._mock_notes_invalid_year_policies_no_rate()
        policies_content = list(filter(lambda note: note.TYPE_ID == 1, notes))[
            0
        ].CONTENT
        rate_content = ""
        result_policies_content, result_rate_content = xform_missing_notes_records_v2(
            audit_header, policies_content, rate_content
        )
        self.assertEqual(policies_content, result_policies_content)
        self.assertEqual(rate_content, result_rate_content)

    def test_xform_missing_notes_records_v2_with_invalid_year_rate_no_policies(self):
        notes, audit_header = self._mock_notes_invalid_year_rate_no_policies()
        policies_content = ""
        rate_content = list(filter(lambda note: note.TYPE_ID == 2, notes))[0].CONTENT
        result_policies_content, result_rate_content = xform_missing_notes_records_v2(
            audit_header, policies_content, rate_content
        )
        self.assertEqual(policies_content, result_policies_content)
        self.assertEqual(rate_content, result_rate_content)

    def test_xform_missing_notes_records_v2_with_invalid_year_no_rate_no_policies(self):
        notes, audit_header = self._mock_notes_invalid_year_no_rate_no_policies()
        policies_content = ""
        rate_content = ""
        result_policies_content, result_rate_content = xform_missing_notes_records_v2(
            audit_header, policies_content, rate_content
        )
        self.assertEqual(policies_content, result_policies_content)
        self.assertEqual(rate_content, result_rate_content)

    def test_xform_missing_notes_records_v2_with_invalid_year_rate_policies(self):
        notes, audit_header = self._mock_notes_invalid_year_rate_policies()
        policies_content = list(filter(lambda note: note.TYPE_ID == 1, notes))[
            0
        ].CONTENT
        rate_content = list(filter(lambda note: note.TYPE_ID == 2, notes))[0].CONTENT
        result_policies_content, result_rate_content = xform_missing_notes_records_v2(
            audit_header, policies_content, rate_content
        )
        self.assertEqual(policies_content, result_policies_content)
        self.assertEqual(rate_content, result_rate_content)

class TestXformRateContent(SimpleTestCase):
    def test_blank_rate_content(self):
        self.assertEqual(xform_rate_content(""), settings.GSA_MIGRATION)

    def test_non_blank_rate_content(self):
        self.assertEqual(xform_rate_content("test_rate"), "test_rate")


class TestXformPoliciesContent(SimpleTestCase):
    def test_blank_policies_content(self):
        self.assertEqual(xform_policies_content(""), settings.GSA_MIGRATION)

    def test_non_blank_policies_content(self):
        self.assertEqual(xform_policies_content("test_policies"), "test_policies")


class TestXformSanitizePoliciesContent(SimpleTestCase):
    def test_special_char_policies_content(self):
        self.assertEqual(xform_sanitize_policies_content("====test_policies"), "test_policies")

    def test_no_special_char_policies_content(self):
        self.assertEqual(xform_sanitize_policies_content("test_policies"), "test_policies")
