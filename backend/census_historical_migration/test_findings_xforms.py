from django.conf import settings
from django.test import SimpleTestCase

from .workbooklib.findings_text import xform_add_placeholder_for_missing_references

from .workbooklib.findings import (
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
