from .errors import (
    err_missing_or_extra_references,
)
from audit.fixtures.excel import (
    SECTION_NAMES,
)


def check_ref_number_in_cap(sac_dict, *_args, **_kwargs):
    """
    Check that all reference numbers in Federal Award Audit Findings workbook
    appear at least once in the Corrective Action Plan workbook.
    """

    all_sections = sac_dict.get("sf_sac_sections", {})
    findings_uniform_guidance_section = (
        all_sections.get("findings_uniform_guidance") or {}
    )
    findings_uniform_guidance = findings_uniform_guidance_section.get(
        "findings_uniform_guidance_entries", []
    )
    corrective_action_plan_section = all_sections.get("corrective_action_plan") or {}
    corrective_action_plan = corrective_action_plan_section.get(
        "corrective_action_plan_entries", []
    )

    declared_references = set()
    in_use_references = set()
    errors = []

    for finding in findings_uniform_guidance:
        ref_number = finding["findings"]["reference_number"]
        if ref_number:
            declared_references.add(ref_number)

    for cap in corrective_action_plan:
        ref_number = cap["reference_number"]
        if ref_number:
            in_use_references.add(ref_number)

    # Items in declared_references but not in in_use_references
    declared_not_in_use = declared_references.difference(in_use_references)

    # Items in in_use_references but not in declared_references
    in_use_not_declared = in_use_references.difference(declared_references)

    if declared_not_in_use or in_use_not_declared:
        errors.append(
            {
                "error": err_missing_or_extra_references(
                    declared_not_in_use,
                    in_use_not_declared,
                    SECTION_NAMES.CORRECTIVE_ACTION_PLAN,
                )
            }
        )
    return errors
