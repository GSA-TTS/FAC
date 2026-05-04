import os
import importlib
from pathlib import Path

from model_bakery import baker
from audit.models import SingleAuditChecklist
from audit.cross_validation.sac_validation_shape import sac_validation_shape
from audit.cross_validation import (
    check_additional_eins,
    check_additional_ueis,
    check_award_reference_uniqueness,
    check_award_ref_declaration,
    check_award_ref_existence,
    check_biennial_low_risk,
    check_certifying_contacts,
    check_ein_attestations,
    check_expenditure_threshold_met,
    check_findings_count_consistency,
    check_finding_prior_references,
    check_finding_reference_uniqueness,
    check_has_federal_awards,
    check_ref_number_in_cap,
    check_ref_number_in_findings_text,
    check_secondary_auditors,
)

validation_functions = [
    check_additional_eins,
    check_additional_ueis,
    check_award_reference_uniqueness,
    check_award_ref_declaration,
    check_award_ref_existence,
    check_biennial_low_risk,
    check_certifying_contacts,
    check_ein_attestations,
    check_expenditure_threshold_met,
    check_findings_count_consistency,
    check_finding_prior_references,
    check_finding_reference_uniqueness,
    check_has_federal_awards,
    check_ref_number_in_cap,
    check_ref_number_in_findings_text,
    check_secondary_auditors,
]


def run_validations(sac_obj):
    shape = sac_validation_shape(sac_obj)
    all_errors = []
    for module in validation_functions:
        try:
            if hasattr(module, "run"):
                results = module.run(shape)
                if results:
                    all_errors.extend(results)
        except Exception as e:
            all_errors.append({"error": f"Error running {module.__name__}: {e}"})
    return all_errors


def main():
    print("=== FAC Workbook Validator ===")
    uei = input("Enter UEI: ")

    # Simulate audit setup
    sac = baker.make(
        SingleAuditChecklist,
        general_information={
            "auditee_uei": uei,
            "auditee_fiscal_period_start": "2024-01-01",
        },
        findings_uniform_guidance={
            "FindingsUniformGuidance": {
                "auditee_uei": uei,
                "findings_uniform_guidance_entries": [],
            }
        },
    )

    # Run validation
    print("Running validations...")
    errors = run_validations(sac)

    if not errors:
        print("\n✅ No validation errors found.")
    else:
        print("\n❌ Validation Errors:")
        for err in errors:
            print("-", err.get("error", str(err)))


if __name__ == "__main__":
    main()
