from .errors import (
    err_prior_no_report,
    err_bad_repeat_prior_reference,
    err_prior_ref_not_found,
)
from dissemination.models import (
    Finding,
    General,
)

from datetime import date


def check_finding_prior_references(sac_dict, *_args, **_kwargs):
    """
    Check that prior references point to reference numbers that actually exist
    in the previous year's report
    """
    all_sections = sac_dict.get("sf_sac_sections")
    findings_uniform_guidance_section = (
        all_sections.get("findings_uniform_guidance") or {}
    )
    findings_uniform_guidance = findings_uniform_guidance_section.get(
        "findings_uniform_guidance_entries", []
    )
    all_prior_refs = _get_prior_refs(findings_uniform_guidance)

    if not all_prior_refs:
        return []

    general_information = all_sections.get("general_information")
    auditee_uei = general_information["auditee_uei"]
    previous_year = (
        date.fromisoformat(general_information["auditee_fiscal_period_start"]).year - 1
    )

    # UEIs only become reliable as of 2022, so don't bother validating
    # prior references before that
    if previous_year < 2022:
        return []

    try:
        previous_year_report = General.objects.get(
            audit_year=previous_year,
            auditee_uei=auditee_uei,
        )
    except General.DoesNotExist:
        return [
            {
                "error": err_prior_no_report(auditee_uei, previous_year),
            }
        ]

    previous_year_report_id = previous_year_report.report_id
    errors = []

    for award_ref, prior_refs_strings in all_prior_refs.items():
        prior_refs = prior_refs_strings.split(",")

        for prior_ref in prior_refs:
            if prior_ref == "N/A":
                errors.append(
                    {
                        "error": err_bad_repeat_prior_reference(award_ref),
                    }
                )
                continue

            if not Finding.objects.filter(
                report_id=previous_year_report_id,
                reference_number=prior_ref,
            ).exists():
                errors.append(
                    {
                        "error": err_prior_ref_not_found(
                            prior_ref, previous_year_report_id
                        ),
                    }
                )

    return errors


def _get_prior_refs(findings_uniform_guidance):
    """
    Returns a dict that maps award references to a list of prior references
    strings
    """
    all_prior_refs = {}

    for finding in findings_uniform_guidance:
        if finding["findings"]["repeat_prior_reference"] == "Y":
            award_ref = finding["program"]["award_reference"]
            cur_prior_refs = finding["findings"]["prior_references"]
            all_prior_refs[award_ref] = cur_prior_refs

    return all_prior_refs
