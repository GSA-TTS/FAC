from unittest import TestCase
from audit.models import Audit
from .audit_validation_shape import audit_validation_shape
from .utils import generate_random_integer
from .check_award_ref_declaration import check_award_ref_declaration
from .errors import err_award_ref_not_declared
from model_bakery import baker


class CheckAwardRefDeclarationTests(TestCase):
    def setUp(self):
        """Set up the common variables for the test cases."""
        self.AWARD_MIN = 1000
        self.AWARD_MAX = 1500
        self.AUDITEE_UEI = "AAA123456BBB"
        self.award1 = {
            "award_reference": f"AWARD-{generate_random_integer(self.AWARD_MIN, self.AWARD_MAX)}"
        }
        self.award2 = {
            "award_reference": f"AWARD-{generate_random_integer(self.AWARD_MIN * 2, self.AWARD_MAX * 2)}"
        }
        self.award3 = {
            "award_reference": f"AWARD-{generate_random_integer(self.AWARD_MIN * 3, self.AWARD_MAX * 3)}"
        }
        self.award_with_longer_ref = {"award_reference": "AWARD-00123"}
        self.award_with_shorter_ref = {"award_reference": "AWARD-0123"}

    @staticmethod
    def _make_federal_awards(award_refs) -> dict:
        return {"federal_awards": {"awards": award_refs}}

    def _make_findings_uniform_guidance(self, award_refs) -> dict:
        return {"findings_uniform_guidance": [{"program": ref} for ref in award_refs]}

    def _make_audit(self, award_refs, findings_award_refs) -> Audit:
        audit_data = {
            **self._make_federal_awards(award_refs),
            **self._make_findings_uniform_guidance(findings_award_refs),
        }
        return baker.make(Audit, version=0, audit=audit_data)

    def test_no_errors_for_matching_award_references(self):
        """When the set of award references in both the Federal Awards workbook and the Federal
        Awards Audit Findings workbook match, no errors should be raised."""
        award_refs = [self.award1, self.award2]
        audit = self._make_audit(award_refs, award_refs)
        errors = check_award_ref_declaration(audit_validation_shape(audit))
        self.assertEqual(errors, [])

    def test_no_errors_for_subset_award_references_in_findings(self):
        """When the set of award references in the Federal Awards Audit Findings workbook is
        a subset of the set of award references in the Federal Awards workbook, no errors should be raised.
        """
        audit = self._make_audit(
            [self.award1, self.award2, self.award3], [self.award1, self.award3]
        )
        errors = check_award_ref_declaration(audit_validation_shape(audit))
        self.assertEqual(errors, [])

    def test_errors_for_findings_with_undeclared_award_refs(self):
        """When the set of award references in the Federal Awards Audit Findings workbook is not
        a subset of the set of award references in the Federal Awards workbook, errors should be raised.
        """
        audit = self._make_audit([self.award1, self.award3], [self.award1, self.award2])
        errors = check_award_ref_declaration(audit_validation_shape(audit))
        self.assertEqual(len(errors), 1)
        expected_error = err_award_ref_not_declared([self.award2["award_reference"]])
        self.assertIn({"error": expected_error}, errors)

    def test_padding_when_declared_award_ref_max_length_greater(self):
        """Test case where declared award reference length is greater than reported award reference length."""
        audit = self._make_audit(
            [self.award_with_longer_ref], [self.award_with_shorter_ref]
        )
        errors = check_award_ref_declaration(audit_validation_shape(audit))
        # No errors expected
        self.assertEqual(errors, [])

    def test_padding_when_reported_award_ref_max_length_greater(self):
        """Test case where reported award reference length is greater than declared award reference length."""
        audit = self._make_audit(
            [self.award_with_shorter_ref], [self.award_with_longer_ref]
        )
        errors = check_award_ref_declaration(audit_validation_shape(audit))
        # No errors expected
        self.assertEqual(errors, [])
