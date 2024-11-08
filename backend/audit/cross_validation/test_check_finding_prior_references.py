from django.test import TestCase
from model_bakery import baker

from .check_finding_prior_references import (
    check_finding_prior_references,
    _get_prior_refs,
)
from .sac_validation_shape import sac_validation_shape
from audit.models import SingleAuditChecklist
from dissemination.models import (
    Finding,
    General,
)

from datetime import date


class CheckFindingPriorReferencesTests(TestCase):
    def _test_check_finding_prior_references(
        self,
        auditee_fiscal_period_start,  # ISO date string
        awards_prior_refs,  # Dict of award # -> prior reference string
        prior_report_exists,  # Bool determining if prior report should exist in General
        repeat_prior_reference,  # Set 'Y' or 'N' in findings_uniform_guidance_entries
        expected_error_strs,  # List of error strings
    ):
        """
        Helper used for testing prior references
        """
        AUDITEE_UEI = "ABC123DEF456"

        # Set up the awards for the sac being validated
        findings_uniform_guidance_entries = []
        for award_ref, prior_refs_str in awards_prior_refs.items():
            findings_uniform_guidance_entries.append(
                {
                    "program": {"award_reference": award_ref},
                    "findings": {
                        "repeat_prior_reference": repeat_prior_reference,
                        "prior_references": prior_refs_str,
                    },
                }
            )

        # Create the sac using awards created
        new_sac = baker.make(
            SingleAuditChecklist,
            general_information={
                "auditee_uei": AUDITEE_UEI,
                "auditee_fiscal_period_start": auditee_fiscal_period_start,
            },
            findings_uniform_guidance={
                "FindingsUniformGuidance": {
                    "auditee_uei": "ABB123456CCC",
                    "findings_uniform_guidance_entries": findings_uniform_guidance_entries,
                }
            },
        )
        new_sac.save()

        if prior_report_exists:
            # Create the prior report that was submitted last year
            previous_year = date.fromisoformat(auditee_fiscal_period_start).year - 1
            prior_gen = baker.make(
                General,
                report_id="foo-report-id",
                audit_year=previous_year,
                auditee_uei=AUDITEE_UEI,
            )
            prior_gen.save()

            # Generate the findings needed to be associated with the report
            for award_ref, prior_refs_str in awards_prior_refs.items():
                prior_refs = prior_refs_str.split(",")
                for prior_ref in prior_refs:
                    prior_finding = baker.make(
                        Finding,
                        report_id=prior_gen,
                        reference_number=prior_ref,
                    )
                    prior_finding.save()

        result = check_finding_prior_references(sac_validation_shape(new_sac))

        self.assertEqual(expected_error_strs, result)

    def test_check_finding_prior_references_single_prior(self):
        """
        One award having a single prior reference should pass
        """
        self._test_check_finding_prior_references(
            auditee_fiscal_period_start="2001-01-01",
            awards_prior_refs={
                "AWARD-001": "2000-777",
            },
            repeat_prior_reference="Y",
            prior_report_exists=True,
            expected_error_strs=[],
        )

    def test_check_finding_prior_references_multiple_priors(self):
        """
        One award having multiple prior references should pass
        """
        self._test_check_finding_prior_references(
            auditee_fiscal_period_start="2001-01-01",
            awards_prior_refs={
                "AWARD-001": "2000-777,2000-888",
            },
            repeat_prior_reference="Y",
            prior_report_exists=True,
            expected_error_strs=[],
        )

    def test_check_finding_prior_references_multiple_awards(self):
        """
        Multiple awards having prior references should pass
        """
        self._test_check_finding_prior_references(
            auditee_fiscal_period_start="2001-01-01",
            awards_prior_refs={
                "AWARD-001": "2000-777",
                "AWARD-002": "2000-888",
            },
            repeat_prior_reference="Y",
            prior_report_exists=True,
            expected_error_strs=[],
        )

    def test_check_finding_prior_references_n_a_with_y(self):
        """
        An award having no prior references but repeat_prior_reference set to
        'Y' should fail
        """
        self._test_check_finding_prior_references(
            auditee_fiscal_period_start="2001-01-01",
            awards_prior_refs={
                "AWARD-001": "N/A",
            },
            repeat_prior_reference="Y",
            prior_report_exists=True,
            expected_error_strs=[
                {
                    "error": "AWARD-001 field repeat_prior_reference is set to 'Y', but prior_references is set to 'N/A'.",
                }
            ],
        )

    def test_check_finding_prior_references_no_prior_report(self):
        """
        An award having a prior reference but no prior report exists should fail
        """
        self._test_check_finding_prior_references(
            auditee_fiscal_period_start="2001-01-01",
            awards_prior_refs={
                "AWARD-001": "2000-777",
            },
            repeat_prior_reference="Y",
            prior_report_exists=False,
            expected_error_strs=[
                {
                    "error": "Findings uniform guidance contains prior reference numbers, but no report was found for UEI ABC123DEF456 in the previous year (2000).",
                }
            ],
        )

    def test_get_prior_refs(self):
        """
        Extracting prior_references from an award should pass
        """
        findings_uniform_guidance = [
            {
                "program": {"award_reference": "AWARD-001"},
                "findings": {
                    "repeat_prior_reference": "Y",
                    "prior_references": "2022-033",
                },
            },
        ]

        results = _get_prior_refs(findings_uniform_guidance)

        self.assertEqual(results, {"AWARD-001": "2022-033"})

    def test_get_prior_refs_multiple_awards(self):
        """
        Extracting prior_references from multiple awards should pass
        """
        findings_uniform_guidance = [
            {
                "program": {"award_reference": "AWARD-001"},
                "findings": {
                    "repeat_prior_reference": "Y",
                    "prior_references": "2022-033",
                },
            },
            {
                "program": {"award_reference": "AWARD-002"},
                "findings": {
                    "repeat_prior_reference": "Y",
                    "prior_references": "2022-022",
                },
            },
        ]

        results = _get_prior_refs(findings_uniform_guidance)

        self.assertEqual(results, {"AWARD-001": "2022-033", "AWARD-002": "2022-022"})

    def test_get_prior_refs_no_repeat_prior_reference(self):
        """
        Extracting prior_references should only occur when repeat_prior_reference
        is 'Y'
        """
        findings_uniform_guidance = [
            {
                "program": {"award_reference": "AWARD-001"},
                "findings": {
                    "repeat_prior_reference": "Y",
                    "prior_references": "2022-033",
                },
            },
            {
                "program": {"award_reference": "AWARD-002"},
                "findings": {
                    "repeat_prior_reference": "N",
                    "prior_references": "N/A",
                },
            },
        ]

        results = _get_prior_refs(findings_uniform_guidance)

        self.assertEqual(results, {"AWARD-001": "2022-033"})

    def test_get_prior_refs_no_awards(self):
        """
        Extracting prior_references when there are no awards should pass
        """
        findings_uniform_guidance = []

        results = _get_prior_refs(findings_uniform_guidance)

        self.assertEqual(results, {})
