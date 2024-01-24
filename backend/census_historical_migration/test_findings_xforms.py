from django.test import SimpleTestCase

from .workbooklib.findings import xform_sort_compliance_requirement


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
