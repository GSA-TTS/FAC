from django.conf import settings
from django.test import SimpleTestCase

from .exception_utils import DataMigrationError
from .workbooklib.notes_to_sefa import (
    xform_is_minimis_rate_used,
    xform_missing_note_title_and_content,
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
        ):
            self.TITLE = TITLE
            self.CONTENT = CONTENT

    def _mock_notes_no_title(self):
        notes = []
        notes.append(
            self.MockNote(
                TITLE="",
                CONTENT="SUPPORTIVE HOUSING FOR THE ELDERLY (14.157) - Balances outstanding at the end of the audit period were 3356.",
            )
        )
        notes.append(
            self.MockNote(
                TITLE="",
                CONTENT="MORTGAGE INSURANCE FOR THE PURCHASE OR REFINANCING OF EXISTING MULTIFAMILY HOUSING PROJECTS (14.155) - Balances outstanding at the end of the audit period were 4040.",
            )
        )
        return notes

    def _mock_notes_no_content(self):
        notes = []
        notes.append(
            self.MockNote(
                TITLE="Loan/loan guarantee outstanding balances",
                CONTENT="",
            )
        )
        notes.append(
            self.MockNote(
                TITLE="Federally Funded Insured Mortgages and Capital Advances",
                CONTENT="",
            )
        )
        return notes

    def _mock_notes_with_title_content(self):
        notes = []
        notes.append(
            self.MockNote(
                TITLE="Loan/loan guarantee outstanding balances",
                CONTENT="SUPPORTIVE HOUSING FOR THE ELDERLY (14.157) - Balances outstanding at the end of the audit period were 4000.",
            )
        )
        notes.append(
            self.MockNote(
                TITLE="Federally Funded Insured Mortgages and Capital Advances",
                CONTENT="MORTGAGE INSURANCE FOR THE PURCHASE OR REFINANCING OF EXISTING MULTIFAMILY HOUSING PROJECTS (14.155) - Balances outstanding at the end of the audit period were 5000.",
            )
        )
        return notes

    def test_note_w_no_title(self):
        notes = self._mock_notes_no_title()
        result = xform_missing_note_title_and_content(notes)
        self.assertIn(settings.GSA_MIGRATION, result[0].TITLE)
        self.assertIn(settings.GSA_MIGRATION, result[1].TITLE)
        self.assertNotIn(settings.GSA_MIGRATION, result[0].CONTENT)
        self.assertNotIn(settings.GSA_MIGRATION, result[1].CONTENT)

    def test_note_w_no_content(self):
        notes = self._mock_notes_no_content()
        result = xform_missing_note_title_and_content(notes)
        self.assertNotIn(settings.GSA_MIGRATION, result[0].TITLE)
        self.assertNotIn(settings.GSA_MIGRATION, result[1].TITLE)
        self.assertIn(settings.GSA_MIGRATION, result[0].CONTENT)
        self.assertIn(settings.GSA_MIGRATION, result[1].CONTENT)

    def test_note_with_title_content(self):
        notes = self._mock_notes_with_title_content()
        result = xform_missing_note_title_and_content(notes)
        self.assertNotIn(settings.GSA_MIGRATION, result[0].TITLE)
        self.assertNotIn(settings.GSA_MIGRATION, result[1].TITLE)
        self.assertNotIn(settings.GSA_MIGRATION, result[0].CONTENT)
        self.assertNotIn(settings.GSA_MIGRATION, result[1].CONTENT)
