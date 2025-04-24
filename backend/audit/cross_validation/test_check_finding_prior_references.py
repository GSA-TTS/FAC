from django.test import TestCase
from model_bakery import baker

from .audit_validation_shape import audit_validation_shape
from .check_finding_prior_references import (
    check_finding_prior_references,
    _get_prior_refs,
)
from ..models import Audit, AuditValidationWaiver


class CheckFindingPriorReferencesTests(TestCase):
    def _test_check_finding_prior_references(
        self,
        auditee_fiscal_period_start,  # ISO date string
        awards_prior_refs,  # Dict of award # -> prior reference string
        repeat_prior_reference,  # Bool to set 'Y' or 'N' in findings_uniform_guidance_entries
        prior_refs_exist,  # Bool for if prior references should actually exist
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

        audit_data = {
            "general_information": {
                "auditee_uei": AUDITEE_UEI,
                "auditee_fiscal_period_start": auditee_fiscal_period_start,
            },
            "findings_uniform_guidance": findings_uniform_guidance_entries,
        }
        audit = baker.make(Audit, version=0, audit=audit_data)

        # Create the sac using awards created
        if use_waiver:
            baker.make(
                AuditValidationWaiver,
                report_id=audit,
                waiver_types=[AuditValidationWaiver.TYPES.PRIOR_REFERENCES],
            )
            audit.waiver_types = [AuditValidationWaiver.TYPES.PRIOR_REFERENCES]
        audit.save()

        # Create the prior reports for each year provided
        for year in prior_report_years:
            audit_data = {
                "audit_year": year,
                "general_information": {
                    "auditee_uei": AUDITEE_UEI,
                },
            }
            if prior_refs_exist:
                findings = self._generate_findings(awards_prior_refs, year)
                audit_data = audit_data | {
                    "findings_uniform_guidance": findings,
                }
            baker.make(
                Audit, version=0, report_id=f"foo-report-id-{year}", audit=audit_data
            )

        shaped_audit = audit_validation_shape(audit)
        result = check_finding_prior_references(shaped_audit)

        self.assertEqual(expected_error_strs, result)

    @staticmethod
    def _generate_findings(awards_prior_refs, year):
        prior_findings = []
        for award_ref, prior_refs_str in awards_prior_refs.items():
            prior_refs = prior_refs_str.split(",")
            for prior_ref in prior_refs:
                prior_year = prior_ref[:4]
                if prior_year == year:
                    prior_findings.append({"findings": {"reference_number": prior_ref}})
        return prior_findings

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
            prior_refs_exist=True,
            prior_report_years=["2023"],
            use_waiver=False,
            expected_error_strs=[],
        )

    def test_check_finding_prior_references_before_2022(self):
        """
        One award having a non-existent prior reference that's before
        2022 should still pass
        """
        self._test_check_finding_prior_references(
            auditee_fiscal_period_start="2024-01-01",
            awards_prior_refs={
                "AWARD-001": "2021-777",
            },
            repeat_prior_reference="Y",
            prior_refs_exist=True,
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
            prior_refs_exist=True,
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
            prior_refs_exist=True,
            prior_report_years=["2022", "2023"],
            use_waiver=False,
            expected_error_strs=[],
        )

    def test_check_finding_prior_references_no_prior_ref(self):
        """
        An award having a prior reference that doesn't exist should fail
        """
        self._test_check_finding_prior_references(
            auditee_fiscal_period_start="2024-01-01",
            awards_prior_refs={
                "AWARD-001": "2023-777",
            },
            repeat_prior_reference="Y",
            prior_refs_exist=False,
            prior_report_years=["2023"],
            use_waiver=False,
            expected_error_strs=[
                {
                    "error": "The Federal Awards Audit Findings workbook contains prior "
                    + "reference 2023-777 (award AWARD-001, row 2). However, that "
                    + "reference was not found in any previous reports for UEI "
                    + "ABC123DEF456.",
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
            prior_refs_exist=True,
            prior_report_years=[],
            use_waiver=False,
            expected_error_strs=[
                {
                    "error": "The Federal Awards Audit Findings workbook contains prior "
                    + "reference 2023-777 (award AWARD-001, row 2). However, that "
                    + "reference was not found in any previous reports for UEI "
                    + "ABC123DEF456.",
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
            prior_refs_exist=False,
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
