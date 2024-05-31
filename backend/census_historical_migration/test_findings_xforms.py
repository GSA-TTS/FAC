from django.conf import settings
from django.test import SimpleTestCase

from census_historical_migration.invalid_migration_tags import INVALID_MIGRATION_TAGS
from census_historical_migration.invalid_record import InvalidRecord

from .workbooklib.findings_text import (
    xform_add_placeholder_for_missing_text_of_finding,
    xform_add_placeholder_for_missing_references,
)

from .workbooklib.findings import (
    has_duplicate_ref_numbers,
    track_invalid_records_with_repeated_ref_numbers,
    xform_empty_repeat_prior_reference,
    xform_replace_required_fields_with_gsa_migration_when_empty,
    xform_sort_compliance_requirement,
    xform_missing_compliance_requirement,
)


class TestXformSortComplianceRequirement(SimpleTestCase):
    class Finding:
        def __init__(self, typerequirement):
            self.TYPEREQUIREMENT = typerequirement

    def test_sort_and_uppercase(self):
        """Test that strings are sorted and uppercased."""
        findings = [self.Finding("abc"), self.Finding(" fca"), self.Finding("Bac")]
        expected_results = ["ABC", "ACF", "ABC"]

        xform_sort_compliance_requirement(findings)

        for finding, expected in zip(findings, expected_results):
            self.assertEqual(finding.TYPEREQUIREMENT, expected)

    def test_empty_string(self):
        """Test that an empty string is not changed."""
        findings = [self.Finding("")]
        xform_sort_compliance_requirement(findings)
        self.assertEqual(findings[0].TYPEREQUIREMENT, "")

    def test_no_change_needed(self):
        """Test that a string that is already sorted and uppercased is not changed."""
        findings = [self.Finding("ABC")]
        xform_sort_compliance_requirement(findings)
        self.assertEqual(findings[0].TYPEREQUIREMENT, "ABC")

    def test_with_spaces_and_case(self):
        """Test that strings with spaces and mixed case are sorted and uppercased."""
        findings = [self.Finding(" aBc "), self.Finding("CBA "), self.Finding("bAc ")]
        expected_results = ["ABC", "ABC", "ABC"]

        xform_sort_compliance_requirement(findings)

        for finding, expected in zip(findings, expected_results):
            self.assertEqual(finding.TYPEREQUIREMENT, expected)


class TestXformAddPlaceholderForMissingFindingsText(SimpleTestCase):
    class Findings:
        def __init__(self, refnum):
            self.FINDINGREFNUMS = refnum

    class FindingsText:
        def __init__(self, refnum, seqnum=None, text=None, chartstables=None):
            self.FINDINGREFNUMS = refnum
            self.SEQ_NUMBER = seqnum
            self.TEXT = text
            self.CHARTSTABLES = chartstables

    def test_placeholder_addition_for_missing_references(self):
        # Setup specific test data
        mock_findings = [
            self.Findings("ref1"),
            self.Findings("ref2"),
        ]
        mock_findings_texts = [
            self.FindingsText("ref1", "1", "text1", "chart1"),
        ]

        findings_texts = xform_add_placeholder_for_missing_references(
            mock_findings, mock_findings_texts
        )

        self.assertEqual(
            len(findings_texts), 2
        )  # Expecting two items in findings_texts
        self.assertEqual(findings_texts[1].FINDINGREFNUMS, "ref2")
        self.assertEqual(findings_texts[1].TEXT, settings.GSA_MIGRATION)
        self.assertEqual(findings_texts[1].CHARTSTABLES, settings.GSA_MIGRATION)

    def test_no_placeholder_addition_when_all_references_present(self):
        # Setup specific test data
        mock_findings = [
            self.Findings("ref1"),
            self.Findings("ref2"),
        ]
        mock_findings_texts = [
            self.FindingsText("ref1", "1", "text1", "chart1"),
            self.FindingsText("ref2", "2", "text2", "chart2"),
        ]

        findings_texts = xform_add_placeholder_for_missing_references(
            mock_findings, mock_findings_texts
        )

        self.assertEqual(
            len(findings_texts), 2
        )  # Expecting two items in findings_texts
        self.assertEqual(findings_texts[0].FINDINGREFNUMS, "ref1")
        self.assertEqual(findings_texts[1].FINDINGREFNUMS, "ref2")


class TestXformAddPlaceholderForMissingTextOfFinding(SimpleTestCase):

    class FindingsText:
        def __init__(self, FINDINGREFNUMS=None, TEXT=None):
            self.FINDINGREFNUMS = FINDINGREFNUMS
            self.TEXT = TEXT

    def test_add_placeholder_to_empty_text(self):
        findings_texts = [self.FindingsText(FINDINGREFNUMS="123", TEXT="")]
        expected_text = settings.GSA_MIGRATION
        xform_add_placeholder_for_missing_text_of_finding(findings_texts)
        self.assertEqual(
            findings_texts[0].TEXT,
            expected_text,
            "The TEXT field should have the placeholder text.",
        )

    def test_no_placeholder_if_text_present(self):
        findings_texts = [self.FindingsText(FINDINGREFNUMS="123", TEXT="Existing text")]
        expected_text = "Existing text"
        xform_add_placeholder_for_missing_text_of_finding(findings_texts)
        self.assertEqual(
            findings_texts[0].TEXT,
            expected_text,
            "The TEXT field should not be modified.",
        )

    def test_empty_finding_refnums_no_change(self):
        findings_texts = [self.FindingsText(FINDINGREFNUMS="", TEXT="")]
        xform_add_placeholder_for_missing_text_of_finding(findings_texts)
        self.assertEqual(
            findings_texts[0].TEXT,
            "",
            "The TEXT field should remain empty if FINDINGREFNUMS is empty.",
        )


class TestXformMissingComplianceRequirement(SimpleTestCase):
    class Findings:
        def __init__(self, type_requirement):
            self.TYPEREQUIREMENT = type_requirement

    def test_missing_compliance_requirement(self):
        mock_findings = [self.Findings("")]

        xform_missing_compliance_requirement(mock_findings)

        self.assertEqual(mock_findings[0].TYPEREQUIREMENT, settings.GSA_MIGRATION)

    def test_normal_compliance_requirement(self):
        mock_findings = [self.Findings("ABC")]

        xform_missing_compliance_requirement(mock_findings)

        self.assertEqual(mock_findings[0].TYPEREQUIREMENT, "ABC")


class TestHasDuplicateRefNumbers(SimpleTestCase):

    class Finding:
        def __init__(self, FINDINGREFNUMS, ELECAUDITSID):
            self.FINDINGREFNUMS = FINDINGREFNUMS
            self.ELECAUDITSID = ELECAUDITSID

    def test_no_duplicates(self):
        """Test that no duplicates are found when there are no duplicate reference numbers."""
        findings = [self.Finding("ref1", "award1"), self.Finding("ref2", "award2")]
        award_refs = [finding.ELECAUDITSID for finding in findings]
        result = has_duplicate_ref_numbers(award_refs, findings)
        self.assertFalse(result)

    def test_with_duplicates(self):
        """Test that duplicates are found when there are duplicate reference numbers."""
        findings = [self.Finding("ref1", "award1"), self.Finding("ref1", "award1")]
        award_refs = [finding.ELECAUDITSID for finding in findings]
        result = has_duplicate_ref_numbers(award_refs, findings)
        self.assertTrue(result)

    def test_different_awards(self):
        """Test that duplicates are not found when the reference numbers are the same but the awards are different."""
        findings = [self.Finding("ref1", "award1"), self.Finding("ref1", "award2")]
        award_refs = [finding.ELECAUDITSID for finding in findings]
        result = has_duplicate_ref_numbers(award_refs, findings)
        self.assertFalse(result)


class TestTrackInvalidRecordsWithRepeatedRefNumbers(SimpleTestCase):

    class Finding:
        def __init__(self, FINDINGREFNUMS, ELECAUDITSID):
            self.FINDINGREFNUMS = FINDINGREFNUMS
            self.ELECAUDITSID = ELECAUDITSID

    def test_track_invalid_records(self):

        InvalidRecord.reset()
        findings = [self.Finding("ref1", "id1"), self.Finding("ref1", "id1")]
        award_refs = [finding.ELECAUDITSID for finding in findings]
        track_invalid_records_with_repeated_ref_numbers(award_refs, findings)

        self.assertEqual(
            InvalidRecord.fields["finding"],
            [
                [
                    {
                        "census_data": [
                            {"column": "FINDINGREFNUMS", "value": "ref1"},
                            {"column": "ELECAUDITSID", "value": "id1"},
                        ],
                        "gsa_fac_data": {"field": "reference_number", "value": "ref1"},
                    },
                    {
                        "census_data": [
                            {"column": "FINDINGREFNUMS", "value": "ref1"},
                            {"column": "ELECAUDITSID", "value": "id1"},
                        ],
                        "gsa_fac_data": {"field": "reference_number", "value": "ref1"},
                    },
                ]
            ],
        )

        self.assertEqual(
            InvalidRecord.fields["validations_to_skip"],
            ["check_finding_reference_uniqueness"],
        )
        self.assertEqual(
            InvalidRecord.fields["invalid_migration_tag"],
            [INVALID_MIGRATION_TAGS.DUPLICATE_FINDING_REFERENCE_NUMBERS],
        )

    def test_no_invalid_records(self):
        """Test that no invalid records are tracked when there are no duplicate reference numbers."""
        findings = [self.Finding("ref1", "id1"), self.Finding("ref2", "id2")]
        award_refs = [finding.ELECAUDITSID for finding in findings]
        InvalidRecord.reset()

        track_invalid_records_with_repeated_ref_numbers(award_refs, findings)

        self.assertEqual(InvalidRecord.fields["finding"], [])
        self.assertEqual(InvalidRecord.fields["validations_to_skip"], [])


class TestXformReplaceRequiredFields(SimpleTestCase):
    class Finding:
        def __init__(
            self,
            MODIFIEDOPINION,
            OTHERNONCOMPLIANCE,
            MATERIALWEAKNESS,
            SIGNIFICANTDEFICIENCY,
            OTHERFINDINGS,
        ):
            self.MODIFIEDOPINION = MODIFIEDOPINION
            self.OTHERNONCOMPLIANCE = OTHERNONCOMPLIANCE
            self.MATERIALWEAKNESS = MATERIALWEAKNESS
            self.SIGNIFICANTDEFICIENCY = SIGNIFICANTDEFICIENCY
            self.OTHERFINDINGS = OTHERFINDINGS

    def test_replace_empty_fields(self):
        findings = [
            self.Finding(
                MODIFIEDOPINION="",
                OTHERNONCOMPLIANCE="",
                MATERIALWEAKNESS="Present",
                SIGNIFICANTDEFICIENCY="",
                OTHERFINDINGS="Present",
            ),
            self.Finding(
                MODIFIEDOPINION="Present",
                OTHERNONCOMPLIANCE="Present",
                MATERIALWEAKNESS="",
                SIGNIFICANTDEFICIENCY="",
                OTHERFINDINGS="Present",
            ),
            self.Finding(
                MODIFIEDOPINION="",
                OTHERNONCOMPLIANCE="Present",
                MATERIALWEAKNESS="Present",
                SIGNIFICANTDEFICIENCY="",
                OTHERFINDINGS="",
            ),
        ]

        xform_replace_required_fields_with_gsa_migration_when_empty(findings)

        self.assertEqual(findings[0].MODIFIEDOPINION, settings.GSA_MIGRATION)
        self.assertEqual(findings[0].OTHERNONCOMPLIANCE, settings.GSA_MIGRATION)
        self.assertEqual(findings[0].MATERIALWEAKNESS, "Present")
        self.assertEqual(findings[0].SIGNIFICANTDEFICIENCY, settings.GSA_MIGRATION)
        self.assertEqual(findings[0].OTHERFINDINGS, "Present")

        self.assertEqual(findings[1].MODIFIEDOPINION, "Present")
        self.assertEqual(findings[1].OTHERNONCOMPLIANCE, "Present")
        self.assertEqual(findings[1].MATERIALWEAKNESS, settings.GSA_MIGRATION)
        self.assertEqual(findings[1].SIGNIFICANTDEFICIENCY, settings.GSA_MIGRATION)
        self.assertEqual(findings[1].OTHERFINDINGS, "Present")

        self.assertEqual(findings[2].MODIFIEDOPINION, settings.GSA_MIGRATION)
        self.assertEqual(findings[2].OTHERNONCOMPLIANCE, "Present")
        self.assertEqual(findings[2].MATERIALWEAKNESS, "Present")
        self.assertEqual(findings[2].SIGNIFICANTDEFICIENCY, settings.GSA_MIGRATION)
        self.assertEqual(findings[2].OTHERFINDINGS, settings.GSA_MIGRATION)


class TestXformMissingRepeatPriorReference(SimpleTestCase):
    class Finding:
        def __init__(self, PRIORFINDINGREFNUMS, REPEATFINDING):
            self.PRIORFINDINGREFNUMS = PRIORFINDINGREFNUMS
            self.REPEATFINDING = REPEATFINDING

    def test_replace_empty_repeat_finding(self):
        findings = [
            self.Finding(PRIORFINDINGREFNUMS="123", REPEATFINDING=""),
            self.Finding(PRIORFINDINGREFNUMS="", REPEATFINDING=""),
            self.Finding(PRIORFINDINGREFNUMS="456", REPEATFINDING="N"),
            self.Finding(PRIORFINDINGREFNUMS="", REPEATFINDING="Y"),
        ]

        xform_empty_repeat_prior_reference(findings)

        self.assertEqual(findings[0].REPEATFINDING, "Y")
        self.assertEqual(findings[1].REPEATFINDING, "N")
        self.assertEqual(findings[2].REPEATFINDING, "N")
        self.assertEqual(findings[3].REPEATFINDING, "Y")
