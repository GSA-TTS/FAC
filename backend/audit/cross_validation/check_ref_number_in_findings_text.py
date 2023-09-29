from .errors import (
    err_missing_or_extra_references,
)
from audit.fixtures.excel import (
    SECTION_NAMES,
)


def check_ref_number_in_findings_text(sac_dict, *_args, **_kwargs):
    """
    Check that all reference numbers in Federal Award Audit Findings workbook
    appear at least once in the Audit Findings Text workbook.
    """

    all_sections = sac_dict.get("sf_sac_sections", {})
    findings_uniform_guidance_section = (
        all_sections.get("findings_uniform_guidance") or {}
    )
    findings_uniform_guidance = findings_uniform_guidance_section.get(
        "findings_uniform_guidance_entries", []
    )
    findings_text_section = all_sections.get("findings_text") or {}
    findings_text = findings_text_section.get("findings_text_entries", [])

    declared_references = set()
    in_use_references = set()
    errors = []

    for finding in findings_uniform_guidance:
        ref_number = finding["findings"]["reference_number"]
        if ref_number:
            declared_references.add(ref_number)

    for finding in findings_text:
        ref_number = finding["reference_number"]
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
                    SECTION_NAMES.AUDIT_FINDINGS_TEXT,
                )
            }
        )
    return errors
