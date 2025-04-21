from django.conf import settings
from census_historical_migration.invalid_record import InvalidRecord
from django.test import TestCase

from .audit_validation_shape import audit_validation_shape
from .utils import generate_random_integer, make_findings_uniform_guidance
from audit.models import Audit
from .check_ref_number_in_cap import check_ref_number_in_cap
from .errors import err_missing_or_extra_references
from model_bakery import baker
from audit.fixtures.excel import (
    SECTION_NAMES,
)


class CheckRefNumberInCapTests(TestCase):
    def setUp(self):
        """Set up the common variables for the test cases."""
        self.AUDITEE_UEI = "AAA123456BBB"
        self.reference_1 = "2023-100"
        self.reference_2 = "2023-200"
        self.reference_3 = "2023-300"

    def _make_cap(self, refs) -> dict:
        return {"corrective_action_plan": [{"reference_number": ref} for ref in refs]}

    def _make_audit(self, findings_refs, findings_text_refs) -> Audit:
        audit_data = {
            **make_findings_uniform_guidance(findings_refs, self.AUDITEE_UEI),
            **self._make_cap(findings_text_refs),
        }

        return baker.make(Audit, version=0, audit=audit_data)

    def test_references_direct_match(self):
        """When all references match directly, no errors should be raised."""
        audit = self._make_audit(
            [self.reference_1, self.reference_2], [self.reference_1, self.reference_2]
        )
        errors = check_ref_number_in_cap(audit_validation_shape(audit))
        self.assertEqual(errors, [])

    def test_references_match_with_duplicates(self):
        """When all references match but there are duplicates, no errors should be raised."""
        original_references = [self.reference_1, self.reference_2]

        duplicated_references = [
            ref
            for ref in original_references
            for _ in range(generate_random_integer(2, 5))
        ]
        audit = self._make_audit(original_references, duplicated_references)
        errors = check_ref_number_in_cap(audit_validation_shape(audit))
        self.assertEqual(errors, [])

    def test_missing_references(self):
        """When there are missing references, an error should be raised."""
        duplicated_references = [
            ref
            for ref in [self.reference_1]
            for _ in range(generate_random_integer(2, 5))
        ]
        audit = self._make_audit(
            [self.reference_1, self.reference_2, self.reference_3],
            duplicated_references,
        )
        errors = check_ref_number_in_cap(audit_validation_shape(audit))

        self.assertEqual(len(errors), 1)
        expected_error = err_missing_or_extra_references(
            {self.reference_2, self.reference_3},
            None,
            SECTION_NAMES.CORRECTIVE_ACTION_PLAN,
        )
        self.assertIn({"error": expected_error}, errors)

    def test_extra_references(self):
        """When there are extra references, an error should be raised."""
        duplicated_references = [
            ref
            for ref in [self.reference_1, self.reference_2, self.reference_3]
            for _ in range(generate_random_integer(2, 5))
        ]
        audit = self._make_audit([self.reference_1], duplicated_references)
        errors = check_ref_number_in_cap(audit_validation_shape(audit))

        self.assertEqual(len(errors), 1)
        expected_error = err_missing_or_extra_references(
            None,
            {self.reference_2, self.reference_3},
            SECTION_NAMES.CORRECTIVE_ACTION_PLAN,
        )
        self.assertIn({"error": expected_error}, errors)

    def test_missing_and_extra_references(self):
        """When there are missing and extra references, an error should be raised."""

        duplicated_references = [
            ref
            for ref in [self.reference_1, self.reference_3]
            for _ in range(generate_random_integer(2, 5))
        ]
        audit = self._make_audit(
            [self.reference_1, self.reference_2], duplicated_references
        )
        errors = check_ref_number_in_cap(audit_validation_shape(audit))

        self.assertEqual(len(errors), 1)
        expected_error = err_missing_or_extra_references(
            {self.reference_2}, {self.reference_3}, SECTION_NAMES.CORRECTIVE_ACTION_PLAN
        )
        self.assertIn({"error": expected_error}, errors)

    def test_more_cap_references_less_findings_for_historical_captexts(self):
        """When there are extra references, update InvalidRecord and do not raise error."""
        duplicated_references = [
            ref
            for ref in [self.reference_1, self.reference_2, self.reference_3]
            for _ in range(generate_random_integer(2, 5))
        ]
        audit = self._make_audit([], duplicated_references)
        audit.data_source = settings.CENSUS_DATA_SOURCE
        audit.save()

        InvalidRecord.reset()
        InvalidRecord.append_validations_to_skip("check_ref_number_in_cap")

        errors = check_ref_number_in_cap(audit_validation_shape(audit))

        self.assertEqual(errors, [])
