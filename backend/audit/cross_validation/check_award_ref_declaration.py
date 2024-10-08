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
    declared_award_ref_max_length = 0
    reported_award_ref_max_length = 0
    for award in federal_awards:
        award_ref = award.get("award_reference")
        if award_ref:
            declared_award_refs.add(award_ref)
            if len(award_ref) > declared_award_ref_max_length:
                declared_award_ref_max_length = len(award_ref)

    for finding in findings_uniform_guidance:
        award_ref = finding["program"]["award_reference"]
        if award_ref:
            reported_award_refs.add(award_ref)
            if len(award_ref) > reported_award_ref_max_length:
                reported_award_ref_max_length = len(award_ref)

    updated_declared_refs, updated_reported_refs = _normalize_award_ref_lengths(
        declared_award_ref_max_length,
        reported_award_ref_max_length,
        federal_awards,
        findings_uniform_guidance,
    )
    if updated_declared_refs:
        declared_award_refs = updated_declared_refs
    if updated_reported_refs:
        reported_award_refs = updated_reported_refs

    difference = reported_award_refs.difference(declared_award_refs)
    if difference:
        errors.append({"error": err_award_ref_not_declared(list(difference))})

    return errors


def _normalize_award_ref_lengths(
    declared_award_ref_max_length,
    reported_award_ref_max_length,
    federal_awards,
    findings_uniform_guidance,
):
    """
    Normalize the lengths of the award references in the Federal Awards and
    Federal Awards Audit Findings workbooks before validation.
    """
    reported_award_refs = set()
    declared_award_refs = set()
    if declared_award_ref_max_length > reported_award_ref_max_length:
        # This is unlikely to happen, but still a good check. It means
        # that the version of the Federal Awards workbook is newer than
        # the version of the Federal Awards Audit Findings workbook.
        diff = declared_award_ref_max_length - reported_award_ref_max_length
        padding = "0" * diff

        for finding in findings_uniform_guidance:
            award_ref = finding["program"]["award_reference"]
            if award_ref:
                award_ref = (
                    f"{award_ref.split('-')[0]}-{padding}{award_ref.split('-')[1]}"
                )
                reported_award_refs.add(award_ref)
    elif declared_award_ref_max_length < reported_award_ref_max_length:
        # This is more likely to happen. It means the version of
        # the Federal Awards Audit Findings workbook is newer than
        # the version of the Federal Awards workbook.
        diff = reported_award_ref_max_length - declared_award_ref_max_length
        padding = "0" * diff

        for award in federal_awards:
            award_ref = award.get("award_reference")
            if award_ref:
                award_ref = (
                    f"{award_ref.split('-')[0]}-{padding}{award_ref.split('-')[1]}"
                )
                declared_award_refs.add(award_ref)
    else:
        # If the lengths are the same, do nothing.
        pass

    return declared_award_refs, reported_award_refs
