from django.test import TestCase
from .utils import generate_random_integer, make_findings_uniform_guidance
from audit.models import SingleAuditChecklist
from .check_ref_number_in_findings_text import check_ref_number_in_findings_text
from .sac_validation_shape import sac_validation_shape
from .errors import err_missing_or_extra_references
from model_bakery import baker
from audit.fixtures.excel import (
    SECTION_NAMES,
)


class CheckRefNumberInFindingsTextTests(TestCase):
    def setUp(self):
        """Set up the common variables for the test cases."""
        self.AUDITEE_UEI = "AAA123456BBB"
        self.reference_1 = "2023-001"
        self.reference_2 = "2023-002"
        self.reference_3 = "2023-003"

    def _make_findings_text(self, refs) -> dict:
        entries = []
        for ref in refs:
            entries.append({"reference_number": ref})
        findings_text = (
            {
                "auditee_uei": self.AUDITEE_UEI,
                "findings_text_entries": entries,
            }
            if len(entries) > 0
            else {"auditee_uei": self.AUDITEE_UEI}
        )
        return {"FindingsText": findings_text}

    def _make_sac(self, findings_refs, findings_text_refs) -> SingleAuditChecklist:
        sac = baker.make(SingleAuditChecklist)
        sac.findings_uniform_guidance = make_findings_uniform_guidance(
            findings_refs, self.AUDITEE_UEI
        )
        sac.findings_text = self._make_findings_text(findings_text_refs)

        return sac

    def test_references_direct_match(self):
        """When all references match directly, no errors should be raised."""
        sac = self._make_sac(
            [self.reference_1, self.reference_2], [self.reference_1, self.reference_2]
        )
        errors = check_ref_number_in_findings_text(sac_validation_shape(sac))
        self.assertEqual(errors, [])

    def test_references_match_with_duplicates(self):
        """When all references match but there are duplicates, no errors should be raised."""
        original_references = [self.reference_1, self.reference_2]
        # Create a list with each reference duplicated n times, where n is generated randomly between 2 and 5
        duplicated_references = [
            ref
            for ref in original_references
            for _ in range(generate_random_integer(2, 5))
        ]
        sac = self._make_sac(original_references, duplicated_references)
        errors = check_ref_number_in_findings_text(sac_validation_shape(sac))
        self.assertEqual(errors, [])

    def test_missing_references(self):
        """When there are missing references, an error should be raised."""
        duplicated_references = [
            ref
            for ref in [self.reference_1]
            for _ in range(generate_random_integer(2, 5))
        ]
        sac = self._make_sac(
            [self.reference_1, self.reference_2, self.reference_3],
            duplicated_references,
        )
        errors = check_ref_number_in_findings_text(sac_validation_shape(sac))
        # Check if the error list mentions self.reference_2, self.reference_3 as missing from findings_text but present in findings_uniform_guidance
        self.assertEqual(len(errors), 1)
        expected_error = err_missing_or_extra_references(
            {self.reference_2, self.reference_3},
            None,
            SECTION_NAMES.AUDIT_FINDINGS_TEXT,
        )
        self.assertIn({"error": expected_error}, errors)

    def test_extra_references(self):
        """When there are extra references, an error should be raised."""
        duplicated_references = [
            ref
            for ref in [self.reference_1, self.reference_2, self.reference_3]
            for _ in range(generate_random_integer(2, 5))
        ]
        sac = self._make_sac([self.reference_1], duplicated_references)
        errors = check_ref_number_in_findings_text(sac_validation_shape(sac))
        # Check if the error list mentions self.reference_2, self.reference_3 as extra from findings_text but present in findings_uniform_guidance
        self.assertEqual(len(errors), 1)
        expected_error = err_missing_or_extra_references(
            None,
            {self.reference_2, self.reference_3},
            SECTION_NAMES.AUDIT_FINDINGS_TEXT,
        )
        self.assertIn({"error": expected_error}, errors)

    def test_missing_and_extra_references(self):
        """When there are missing and extra references, an error should be raised."""

        duplicated_references = [
            ref
            for ref in [self.reference_1, self.reference_3]
            for _ in range(generate_random_integer(2, 5))
        ]
        sac = self._make_sac(
            [self.reference_1, self.reference_2], duplicated_references
        )
        errors = check_ref_number_in_findings_text(sac_validation_shape(sac))
        # Check if the error list mentions self.reference_2, self.reference_3 as extra from findings_text but present in findings_uniform_guidance
        self.assertEqual(len(errors), 1)
        expected_error = err_missing_or_extra_references(
            {self.reference_2}, {self.reference_3}, SECTION_NAMES.AUDIT_FINDINGS_TEXT
        )
        self.assertIn({"error": expected_error}, errors)
