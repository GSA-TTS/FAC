from .errors import (
    err_duplicate_finding_reference,
)
from collections import defaultdict


def check_finding_reference_uniqueness(sac_dict, *_args, **_kwargs):
    """
    Check the uniqueness of REFERENCE numbers for each AWARD in findings.
    """

    all_sections = sac_dict.get("sf_sac_sections", {})
    findings_uniform_guidance_section = (
        all_sections.get("findings_uniform_guidance") or {}
    )
    findings_uniform_guidance = findings_uniform_guidance_section.get(
        "findings_uniform_guidance_entries", []
    )

    ref_numbers = defaultdict(set)
    duplicate_ref_number = defaultdict(set)
    errors = []

    for finding in findings_uniform_guidance:
        award_ref = finding["program"]["award_reference"]
        ref_number = finding["findings"]["reference_number"]
        if ref_number in ref_numbers[award_ref]:
            duplicate_ref_number[award_ref].add(ref_number)
        ref_numbers[award_ref].add(ref_number)

    for award_ref, ref_nums in duplicate_ref_number.items():
        for ref_num in ref_nums:
            errors.append(
                {
                    "error": err_duplicate_finding_reference(
                        award_ref,
                        ref_num,
                    )
                }
            )

    return errors
