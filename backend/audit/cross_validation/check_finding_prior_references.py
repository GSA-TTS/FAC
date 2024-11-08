from .errors import (
    err_prior_no_report,
    err_bad_repeat_prior_reference,
    err_prior_ref_not_found,
)
from dissemination.models import (
    Finding,
    General,
)


def check_finding_prior_references(sac_dict, *_args, **_kwargs):
    """
    Check that prior references point to reference numbers that actually exist
    in the previous year's report
    """
    all_sections = sac_dict.get("sf_sac_sections", {})
    general_information = all_sections.get("general_information", {})
    previous_year = general_information["audit_year"] - 1
    ein = general_information["ein"]

    try:
        previous_year_report = General.objects.get(
            audit_year=previous_year,
            auditee_ein=ein,
        )
    except General.DoesNotExist:
        return [
            err_prior_no_report(ein, previous_year),
        ]

    findings_uniform_guidance_section = (
        all_sections.get("findings_uniform_guidance") or {}
    )
    findings_uniform_guidance = findings_uniform_guidance_section.get(
        "findings_uniform_guidance_entries", []
    )

    all_prior_ref_numbers = _get_prior_ref_numbers(findings_uniform_guidance)
    if not all_prior_ref_numbers:
        return []

    previous_year_report_id = previous_year_report.report_id
    errors = []

    for award_ref, prior_ref_numbers_strings in all_prior_ref_numbers.items():
        prior_ref_numbers = prior_ref_numbers_strings.split(",")

        for prior_ref_number in prior_ref_numbers:
            if prior_ref_number == "N/A":
                errors.append(
                    err_bad_repeat_prior_reference(award_ref),
                )

            if not Finding.objects.filter(
                report_id=previous_year_report_id,
                reference_number=prior_ref_number,
            ).exists():
                errors.append(
                    err_prior_ref_not_found(prior_ref_number, previous_year_report_id)
                )

    return errors


def _get_prior_ref_numbers(findings_uniform_guidance):
    """
    Returns a dict that maps award references to a list of prior references
    """
    all_prior_ref_numbers = {}

    for finding in findings_uniform_guidance:
        if finding["findings"]["repeat_prior_reference"] == "Y":
            award_ref = finding["program"]["award_reference"]
            cur_prior_ref_numbers = finding["findings"]["prior_references"]
            all_prior_ref_numbers[award_ref] = cur_prior_ref_numbers

    return all_prior_ref_numbers
