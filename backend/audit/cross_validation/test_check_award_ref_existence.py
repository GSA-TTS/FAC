from django.test import TestCase
from audit.models import SingleAuditChecklist
from .check_award_ref_existence import (
    check_award_ref_existence,
    FEDERAL_AWARDS_TEMPLATE,
)
from .sac_validation_shape import sac_validation_shape
from .errors import err_missing_award_reference

from model_bakery import baker


class CheckAwardRefExistenceTest(TestCase):
    def setUp(self):
        """Set up the common variables for the test cases."""
        self.award1 = "AWARD-0001"
        self.award2 = None  # Missing award_reference
        self.award3 = "AWARD-2910"

    def _make_federal_awards(self, award_refs) -> dict:
        return {
            "FederalAwards": {
                "federal_awards": [
                    {
                        "program": {"federal_agency_prefix": "10"},
                        "award_reference": award_ref,
                    }
                    if award_ref
                    else {"program": {"federal_agency_prefix": "22"}}
                    for award_ref in award_refs
                ],
            }
        }

    def _make_sac(self, award_refs) -> SingleAuditChecklist:
        sac = baker.make(SingleAuditChecklist)
        sac.federal_awards = self._make_federal_awards(award_refs)
        return sac

    def test_all_awards_have_references(self):
        """When all awards have a reference, no errors should be raised."""
        sac = self._make_sac([self.award1, self.award3])
        errors = check_award_ref_existence(sac_validation_shape(sac))
        self.assertEqual(errors, [])

    def test_missing_award_references_raise_errors(self):
        """When there are awards missing references, the appropriate errors should be raised."""
        sac = self._make_sac([self.award1, self.award2, self.award3])
        errors = check_award_ref_existence(sac_validation_shape(sac))

        self.assertEqual(len(errors), 1)

        first_row = FEDERAL_AWARDS_TEMPLATE["title_row"]
        row_num = first_row + 2  # 2 = index of award2 in the list of awards + 1

        expected_error = err_missing_award_reference(row_num)

        self.assertIn({"error": expected_error}, errors)
