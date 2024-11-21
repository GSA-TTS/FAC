from django.test import TestCase
from model_bakery import baker

from .check_finding_prior_references import (
    check_finding_prior_references,
    _get_prior_refs,
)
from .sac_validation_shape import sac_validation_shape
from audit.models import SingleAuditChecklist, SacValidationWaiver
from dissemination.models import (
    Finding,
    General,
)


class CheckFindingPriorReferencesTests(TestCase):
    def _test_check_finding_prior_references(
        self,
        auditee_fiscal_period_start,  # ISO date string
        awards_prior_refs,  # Dict of award # -> prior reference string
        repeat_prior_reference,  # Bool to set 'Y' or 'N' in findings_uniform_guidance_entries
        prior_report_years,  # List of years to make prior reports for
        use_waiver,  # Bool for using a validation waiver
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
                "report_id": "new_sac_report_id",
            },
            findings_uniform_guidance={
                "FindingsUniformGuidance": {
                    "auditee_uei": "ABB123456CCC",
                    "findings_uniform_guidance_entries": findings_uniform_guidance_entries,
                }
            },
        )

        if use_waiver:
            baker.make(
                SacValidationWaiver,
                report_id=new_sac,
                waiver_types=[SacValidationWaiver.TYPES.PRIOR_REFERENCES],
            )
            new_sac.waiver_types = [SacValidationWaiver.TYPES.PRIOR_REFERENCES]

        new_sac.save()

        # Create the prior reports for each year provided
        years_to_prior_gen = {}
        for year in prior_report_years:
            prior_gen = baker.make(
                General,
                report_id=f"foo-report-id-{year}",
                audit_year=year,
                auditee_uei=AUDITEE_UEI,
            )
            prior_gen.save()
            years_to_prior_gen[year] = prior_gen

        # Generate the findings needed to be associated with the reports
        for award_ref, prior_refs_str in awards_prior_refs.items():
            prior_refs = prior_refs_str.split(",")
            for prior_ref in prior_refs:
                year = prior_ref[:4]
                if year in years_to_prior_gen:
                    prior_finding = baker.make(
                        Finding,
                        report_id=years_to_prior_gen[year],
                        reference_number=prior_ref,
                    )
                    prior_finding.save()

        result = check_finding_prior_references(sac_validation_shape(new_sac))

        self.assertEqual(expected_error_strs, result)

    def test_check_finding_prior_references_single_prior(self):
        """
        One award having a single prior reference that exists should pass
        """
        self._test_check_finding_prior_references(
            auditee_fiscal_period_start="2024-01-01",
            awards_prior_refs={
                "AWARD-001": "2023-777",
            },
            repeat_prior_reference="Y",
            prior_report_years=["2023"],
            use_waiver=False,
            expected_error_strs=[],
        )

    def test_check_finding_prior_references_before_2022(self):
        """
        One award having a non-existent prior prior reference that's before
        2022 should still pass
        """
        self._test_check_finding_prior_references(
            auditee_fiscal_period_start="2022-01-01",
            awards_prior_refs={
                "AWARD-001": "2021-777",
            },
            repeat_prior_reference="Y",
            prior_report_years=[],
            use_waiver=False,
            expected_error_strs=[],
        )

    def test_check_finding_prior_references_multiple_priors(self):
        """
        One award having multiple prior references that exist should pass
        """
        self._test_check_finding_prior_references(
            auditee_fiscal_period_start="2024-01-01",
            awards_prior_refs={
                "AWARD-001": "2023-777,2023-888",
            },
            repeat_prior_reference="Y",
            prior_report_years=["2023"],
            use_waiver=False,
            expected_error_strs=[],
        )

    def test_check_finding_prior_references_multiple_awards(self):
        """
        Multiple awards having prior references that exist should pass
        """
        self._test_check_finding_prior_references(
            auditee_fiscal_period_start="2024-01-01",
            awards_prior_refs={
                "AWARD-001": "2023-777",
                "AWARD-002": "2022-888",
            },
            repeat_prior_reference="Y",
            prior_report_years=["2022", "2023"],
            use_waiver=False,
            expected_error_strs=[],
        )

    def test_check_finding_prior_references_n_a_with_y(self):
        """
        An award having no prior references but repeat_prior_reference set to
        'Y' should fail
        """
        self._test_check_finding_prior_references(
            auditee_fiscal_period_start="2024-01-01",
            awards_prior_refs={
                "AWARD-001": "N/A",
            },
            repeat_prior_reference="Y",
            prior_report_years=["2023"],
            use_waiver=False,
            expected_error_strs=[
                {
                    "error": "Award AWARD-001 field 'Repeat Findings from Prior Year' is set to 'Y', but the 'Prior Year Audit Finding Reference Number' is set to 'N/A'.",
                }
            ],
        )

    def test_check_finding_prior_references_no_prior_report(self):
        """
        An award having a prior reference but no prior report exists should fail
        """
        self._test_check_finding_prior_references(
            auditee_fiscal_period_start="2024-01-01",
            awards_prior_refs={
                "AWARD-001": "2023-777",
            },
            repeat_prior_reference="Y",
            prior_report_years=[],
            use_waiver=False,
            expected_error_strs=[
                {
                    "error": "Findings uniform guidance contains prior reference numbers, but no related report was found for UEI ABC123DEF456.",
                }
            ],
        )

    def test_check_finding_prior_references_waiver(self):
        """
        Invalid prior references should still pass when a waiver is present
        """
        self._test_check_finding_prior_references(
            auditee_fiscal_period_start="2024-01-01",
            awards_prior_refs={
                "AWARD-001": "N/A",
            },
            repeat_prior_reference="Y",
            prior_report_years=[],
            use_waiver=True,
            expected_error_strs=[],
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
