from unittest import TestCase
from audit.models import SingleAuditChecklist
from .sac_validation_shape import sac_validation_shape
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
            "award_reference": f"AWARD-{generate_random_integer(self.AWARD_MIN,self.AWARD_MAX)}"
        }
        self.award2 = {
            "award_reference": f"AWARD-{generate_random_integer(self.AWARD_MIN *2,self.AWARD_MAX *2)}"
        }
        self.award3 = {
            "award_reference": f"AWARD-{generate_random_integer(self.AWARD_MIN *3,self.AWARD_MAX *3)}"
        }

    def _make_federal_awards(self, award_refs) -> dict:
        return {
            "FederalAwards": {
                "auditee_uei": self.AUDITEE_UEI,
                "federal_awards": award_refs,
            }
        }

    def _make_findings_uniform_guidance(self, award_refs) -> dict:
        entries = []
        for ref in award_refs:
            entries.append({"program": ref})

        findings = (
            {
                "auditee_uei": self.AUDITEE_UEI,
                "findings_uniform_guidance_entries": entries,
            }
            if len(entries) > 0
            else {"auditee_uei": self.AUDITEE_UEI}
        )

        return {"FindingsUniformGuidance": findings}

    def _make_sac(self, award_refs, findings_award_refs) -> SingleAuditChecklist:
        sac = baker.make(SingleAuditChecklist)
        sac.federal_awards = self._make_federal_awards(award_refs)
        sac.findings_uniform_guidance = self._make_findings_uniform_guidance(
            findings_award_refs
        )
        return sac

    def test_no_errors_for_matching_award_references(self):
        """When the set of award references in both the Federal Awards workbook and the Federal
        Awards Audit Findings workbook match, no errors should be raised."""
        award_refs = [self.award1, self.award2]
        sac = self._make_sac(award_refs, award_refs)
        errors = check_award_ref_declaration(sac_validation_shape(sac))
        self.assertEqual(errors, [])

    def test_no_errors_for_subset_award_references_in_findings(self):
        """When the set of award references in the Federal Awards Audit Findings workbook is
        a subset of the set of award references in the Federal Awards workbook, no errors should be raised.
        """
        sac = self._make_sac(
            [self.award1, self.award2, self.award3], [self.award1, self.award3]
        )
        errors = check_award_ref_declaration(sac_validation_shape(sac))
        self.assertEqual(errors, [])

    def test_errors_for_findings_with_undeclared_award_refs(self):
        """When the set of award references in the Federal Awards Audit Findings workbook is not
        a subset of the set of award references in the Federal Awards workbook, errors should be raised.
        """
        sac = self._make_sac([self.award1, self.award3], [self.award1, self.award2])
        errors = check_award_ref_declaration(sac_validation_shape(sac))
        self.assertEqual(len(errors), 1)
        expected_error = err_award_ref_not_declared([self.award2["award_reference"]])
        self.assertIn({"error": expected_error}, errors)
