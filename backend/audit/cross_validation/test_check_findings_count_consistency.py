from django.test import TestCase
from audit.models import Audit
from .audit_validation_shape import audit_validation_shape
from .errors import err_findings_count_inconsistent
from .check_findings_count_consistency import check_findings_count_consistency
from .utils import generate_random_integer
from model_bakery import baker


class CheckFindingsCountConsistencyTests(TestCase):
    AWARD_MIN = 1000
    AWARD_MAX = 2000
    FINDINGS_MIN = 1
    FINDINGS_MAX = 5

    def _make_federal_awards(self, findings_count) -> dict:
        return {
            "federal_awards": {
                "awards": [
                    {
                        "program": {"number_of_audit_findings": findings_count},
                        "award_reference": f"AWARD-{self.AWARD_MIN}",
                    },
                    {
                        "program": {"number_of_audit_findings": findings_count},
                        "award_reference": f"AWARD-{self.AWARD_MAX}",
                    },
                ]
            }
        }

    def _make_findings_uniform_guidance(self, awards, mismatch, padding) -> dict:
        entries = []
        for award in awards["federal_awards"]["awards"]:
            award_reference = award["award_reference"]
            if padding:
                award_reference = f"{award_reference.split('-')[0]}-{padding}{award_reference.split('-')[1]}"
            count = award["program"]["number_of_audit_findings"]
            for _ in range(count + mismatch):
                entries.append({"program": {"award_reference": award_reference}})

        return {"findings_uniform_guidance": entries}

    def _make_audit(self, findings_count, mismatch=0, padding="") -> Audit:
        federal_awards = self._make_federal_awards(findings_count)
        findings_uniform_guidance = self._make_findings_uniform_guidance(
            federal_awards, mismatch, padding
        )
        audit_data = {
            **federal_awards,
            **findings_uniform_guidance,
        }
        return baker.make(Audit, version=0, audit=audit_data)

    def test_zero_findings_count_report(self):
        """Ensure no error is returned for consistent zero findings."""
        audit = self._make_audit(0)
        errors = check_findings_count_consistency(audit_validation_shape(audit))
        self.assertEqual(errors, [])

    def test_findings_count_matches_across_workbooks(self):
        """Ensure no error is returned for consistent findings count."""
        audit = self._make_audit(
            generate_random_integer(self.FINDINGS_MIN, self.FINDINGS_MAX)
        )
        errors = check_findings_count_consistency(audit_validation_shape(audit))
        self.assertEqual(errors, [])

    def _test_findings_count_mismatch(self, base_count, mismatch):
        audit = self._make_audit(base_count, mismatch)
        errors = check_findings_count_consistency(audit_validation_shape(audit))
        federal_awards = audit.audit.get("federal_awards", {}).get("awards", [])
        self.assertEqual(len(errors), len(federal_awards))

        for award in federal_awards:
            award_reference = award["award_reference"]
            expected_error = err_findings_count_inconsistent(
                base_count, base_count + mismatch, award_reference
            )
            self.assertIn({"error": expected_error}, errors)

    def test_reported_findings_exceed_declared_count(self):
        """
        Expect errors when the number of findings in the Federal Awards Audit Findings workbook,
        a.k.a the Findings Uniform Guidance workbook, exceeds those declared in the Federal Awards workbook.
        """
        self._test_findings_count_mismatch(
            generate_random_integer(2, 4), generate_random_integer(1, 2)
        )

    def test_declared_findings_exceed_reported_count(self):
        """
        Expect errors when the number of findings in the Federal Awards workbook
        exceeds those reported in the Federal Awards Audit Findings workbook.
        """
        self._test_findings_count_mismatch(
            generate_random_integer(2, 4), generate_random_integer(-2, -1)
        )

    def test_normalize_award_ref_lengths_with_padding(self):
        """
        Ensure that award reference normalization occurs when declared and reported
        award reference lengths differ. Leading zeros are added appropriately.
        """
        audit = self._make_audit(
            generate_random_integer(self.FINDINGS_MIN, self.FINDINGS_MAX), 0, "0"
        )
        errors = check_findings_count_consistency(audit_validation_shape(audit))
        self.assertEqual(errors, [])
