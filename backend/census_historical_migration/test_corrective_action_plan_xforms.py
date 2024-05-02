from django.conf import settings
from django.test import SimpleTestCase

from .workbooklib.corrective_action_plan import (
    xform_add_placeholder_for_missing_action_planned,
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


class TestXformAddPlaceholderForMissingActionPlanned(SimpleTestCase):
    class CapText:
        def __init__(
            self, SEQ_NUMBER=None, FINDINGREFNUMS=None, TEXT=None, CHARTSTABLES=None
        ):
            self.SEQ_NUMBER = SEQ_NUMBER
            self.FINDINGREFNUMS = FINDINGREFNUMS
            self.TEXT = TEXT
            self.CHARTSTABLES = CHARTSTABLES

    def test_add_placeholder_to_empty_text(self):
        captexts = [self.CapText(FINDINGREFNUMS="123", TEXT="")]
        expected_text = settings.GSA_MIGRATION
        xform_add_placeholder_for_missing_action_planned(captexts)
        self.assertEqual(
            captexts[0].TEXT,
            expected_text,
            "The TEXT field should have the placeholder text.",
        )

    def test_no_placeholder_if_text_present(self):
        captexts = [self.CapText(FINDINGREFNUMS="123", TEXT="Existing text")]
        expected_text = "Existing text"
        xform_add_placeholder_for_missing_action_planned(captexts)
        self.assertEqual(
            captexts[0].TEXT, expected_text, "The TEXT field should not be modified."
        )

    def test_empty_finding_refnums_no_change(self):
        captexts = [self.CapText(FINDINGREFNUMS="", TEXT="")]
        xform_add_placeholder_for_missing_action_planned(captexts)
        self.assertEqual(
            captexts[0].TEXT,
            "",
            "The TEXT field should remain empty if FINDINGREFNUMS is empty.",
        )
