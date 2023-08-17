from django.test import TestCase
from audit.models import SingleAuditChecklist
from .check_award_reference_uniqueness import check_award_reference_uniqueness
from .sac_validation_shape import sac_validation_shape
from .errors import err_duplicate_award_reference
from model_bakery import baker


class CheckAwardReferenceUniquenessTests(TestCase):
    def setUp(self):
        """Set up the common variables for the test cases."""
        self.award1 = {"award_reference": "AWARD-0001"}
        self.award2 = {"award_reference": "AWARD-2219"}
        self.award3 = {"award_reference": "AWARD-2910"}

    def _make_federal_awards(self, award_refs) -> dict:
        return {
            "FederalAwards": {
                "federal_awards": award_refs,
            }
        }

    def _make_sac(self, award_refs) -> SingleAuditChecklist:
        sac = baker.make(SingleAuditChecklist)
        sac.federal_awards = self._make_federal_awards(award_refs)
        return sac

    def test_unique_award_references_raise_no_errors(self):
        """When all award references are unique, no errors should be raised."""
        sac = self._make_sac([self.award1, self.award2, self.award3])
        errors = check_award_reference_uniqueness(sac_validation_shape(sac))
        self.assertEqual(errors, [])

    def test_duplicate_award_references_raise_errors(self):
        """When there are duplicate award references, the appropriate errors should be raised."""
        sac = self._make_sac(
            [self.award1, self.award1, self.award3, self.award3, self.award3]
        )
        errors = errors = check_award_reference_uniqueness(sac_validation_shape(sac))
        self.assertEqual(len(errors), 2)

        errors = check_award_reference_uniqueness(sac_validation_shape(sac))
        expected_error1 = err_duplicate_award_reference(self.award1["award_reference"])
        expected_error2 = err_duplicate_award_reference(self.award3["award_reference"])
        self.assertIn({"error": expected_error1}, errors)
        self.assertIn({"error": expected_error2}, errors)
