from .errors import (
    err_award_ref_not_declared,
)


def check_award_ref_declaration(sac_dict, *_args, **_kwargs):
    """
    Check that the award references reported in the Federal Awards Audit Findings workbook
    are present within the Federal Awards workbook.
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

    declared_award_refs = set()
    reported_award_refs = set()
    errors = []

    for award in federal_awards:
        award_ref = award.get("award_reference")
        if award_ref:
            declared_award_refs.add(award_ref)

    for finding in findings_uniform_guidance:
        award_ref = finding["program"]["award_reference"]
        if award_ref:
            reported_award_refs.add(award_ref)

    difference = reported_award_refs.difference(declared_award_refs)
    if difference:
        errors.append({"error": err_award_ref_not_declared(list(difference))})

    return errors
