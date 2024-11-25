from .errors import (
    err_prior_no_report,
    err_prior_ref_not_found,
)
from dissemination.models import (
    Finding,
    General,
)

from datetime import date


def check_finding_prior_references(sac_dict, *_args, **_kwargs):
    """
    Check that prior references numbers point to findings that actually exist
    in a previously submitted report
    """
    # Importing here to avoid circular import
    from audit.models import SacValidationWaiver

    if SacValidationWaiver.TYPES.PRIOR_REFERENCES in sac_dict.get("waiver_types", []):
        return []

    all_sections = sac_dict.get("sf_sac_sections")
    findings_uniform_guidance_section = (
        all_sections.get("findings_uniform_guidance") or {}
    )
    findings_uniform_guidance = findings_uniform_guidance_section.get(
        "findings_uniform_guidance_entries", []
    )
    all_prior_refs = _get_prior_refs(findings_uniform_guidance)

    # No prior reference numbers to validate
    if not all_prior_refs:
        return []

    general_information = all_sections.get("general_information")
    auditee_uei = general_information["auditee_uei"]
    audit_year = date.fromisoformat(
        general_information["auditee_fiscal_period_start"]
    ).year

    # UEIs only become reliable as of 2022, so don't bother invalidating
    # prior references before that
    if audit_year < 2023:
        return []

    # Get the report_ids for previous reports
    previous_report_ids = General.objects.filter(auditee_uei=auditee_uei).values_list(
        "report_id", flat=True
    )
    errors = []

    # Validate all prior reference numbers for each award
    for award_ref, prior_refs_strings in all_prior_refs.items():
        prior_refs = prior_refs_strings.split(",")
        _validate_prior_refs(
            prior_refs,
            award_ref,
            auditee_uei,
            previous_report_ids,
            errors,
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


def _validate_prior_refs(
    prior_refs, award_ref, auditee_uei, previous_report_ids, errors
):
    """
    Performs validation on the given list of prior reference numbers
    """
    for prior_ref in prior_refs:
        prior_ref_year = prior_ref[:4]

        if prior_ref_year.isnumeric() and int(prior_ref_year) < 2022:
            # Skip validation for pre-UEI prior references
            continue
        elif not previous_report_ids:
            errors.append(
                {
                    "error": err_prior_no_report(auditee_uei, prior_ref),
                }
            )

            continue
        elif not Finding.objects.filter(
            report_id__in=previous_report_ids,
            reference_number=prior_ref,
        ).exists():
            # Error if we can't find the prior finding in previous reports
            errors.append(
                {
                    "error": err_prior_ref_not_found(prior_ref),
                }
            )
