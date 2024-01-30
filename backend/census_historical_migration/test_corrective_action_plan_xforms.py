from django.conf import settings
from django.test import SimpleTestCase

from .workbooklib.corrective_action_plan import (
    xform_add_placeholder_for_missing_references,
)


class TestXformAddPlaceholderForMissingCapText(SimpleTestCase):
    class Findings:
        def __init__(self, refnum):
            self.FINDINGREFNUMS = refnum

    class CapText:
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
            self.CapText("ref1", "1", "text1", "chart1"),
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
            self.CapText("ref1", "1", "text1", "chart1"),
            self.CapText("ref2", "2", "text2", "chart2"),
        ]

        findings_texts = xform_add_placeholder_for_missing_references(
            mock_findings, mock_findings_texts
        )

        self.assertEqual(
            len(findings_texts), 2
        )  # Expecting two items in findings_texts
        self.assertEqual(findings_texts[0].FINDINGREFNUMS, "ref1")
        self.assertEqual(findings_texts[1].FINDINGREFNUMS, "ref2")
