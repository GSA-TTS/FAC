from .errors import (
    err_findings_count_inconsistent,
)
from collections import defaultdict


def check_findings_count_consistency(sac_dict, *_args, **_kwargs):
    """
    Checks that the number of findings mentioned in Federal Awards matches
    the number of findings referenced in Federal Awards Audit Findings.
    """

    all_sections = sac_dict.get("sf_sac_sections", {})
    federal_awards_section = all_sections.get("federal_awards") or {}
    federal_awards = federal_awards_section.get("federal_awards", [])
    findings_uniform_guidance_section = (
        all_sections.get("findings_uniform_guidance") or {}
    )
    findings_uniform_guidance = findings_uniform_guidance_section.get(
        "findings_uniform_guidance_entries", []
    )

    expected_award_refs_count = {}
    found_award_refs_count = defaultdict(int)
    errors = []

    for award in federal_awards:
        award_reference = award.get("award_reference", None)
        if award_reference:
            expected_award_refs_count[award_reference] = award["program"][
                "number_of_audit_findings"
            ]

    for finding in findings_uniform_guidance:
        award_ref = finding["program"]["award_reference"]
        if award_ref in expected_award_refs_count:
            found_award_refs_count[award_ref] += 1

    for award_ref, expected in expected_award_refs_count.items():
        counted = found_award_refs_count[award_ref]
        if counted != expected:
            errors.append(
                {
                    "error": err_findings_count_inconsistent(
                        expected,
                        counted,
                        award_ref,
                    )
                }
            )

    return errors
