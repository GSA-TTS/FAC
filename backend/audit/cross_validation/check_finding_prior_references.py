from django.db import connection
from audit.fixtures.excel import (
    FINDINGS_UNIFORM_TEMPLATE_DEFINITION,
)
from dissemination.models import Finding, General
from .errors import err_prior_ref_not_found

from django.conf import settings

from datetime import date
import json
import logging

logger = logging.getLogger(__name__)


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

    # TODO: Update Post SOC Launch -> Clean-up, the check on Audit can go away
    # imported locally to avoid circular dependencies.
    from audit.models import Audit

    report_id = sac_dict.get("sf_sac_meta", {}).get("report_id")
    use_audit = Audit.objects.find_audit_or_none(report_id=report_id) is not None
    previous_findings_refs = None
    if use_audit:
        previous_findings_refs = _get_previous_findings(report_id, auditee_uei)

    # Get the report_ids for previous reports
    previous_report_ids = General.objects.filter(auditee_uei=auditee_uei).values_list(
        "report_id", flat=True
    )
    errors = []
    audit_errors = []
    # Validate all prior reference numbers for each award
    for award_ref, prior_refs_strings in all_prior_refs.items():
        prior_refs = prior_refs_strings.split(",")
        if use_audit:
            _validate_prior_refs_audit(
                prior_refs,
                award_ref,
                auditee_uei,
                previous_findings_refs,
                audit_errors,
            )

        _validate_prior_refs(
            prior_refs,
            award_ref,
            auditee_uei,
            previous_report_ids,
            errors,
        )
    if use_audit:
        _compare_errors(audit_errors, errors)

    return errors


def _get_previous_findings(report_id, auditee_uei):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            select distinct (findings->'findings'->'reference_number') as reference_number
            from audit_audit,
                 jsonb_array_elements(audit->'findings_uniform_guidance') as findings
            where auditee_uei = %s and
                  report_id != %s
        """,
            [auditee_uei, report_id],
        )
        return set([row[0].replace('"', "") for row in cursor.fetchall()])


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


TEMPLATE_DEFINITION_PATH = (
    settings.XLSX_TEMPLATE_JSON_DIR / FINDINGS_UNIFORM_TEMPLATE_DEFINITION
)
FINDINGS_TEMPLATE = json.loads(TEMPLATE_DEFINITION_PATH.read_text(encoding="utf-8"))


# TODO: Update Post SOC Launch -> only the audit version needs to remain
def _validate_prior_refs_audit(
    prior_refs, award_ref, auditee_uei, previous_findings, errors
):
    """
    Performs validation on the given list of prior reference numbers
    """
    first_row = FINDINGS_TEMPLATE["title_row"]

    for index, prior_ref in enumerate(prior_refs):
        current_row = first_row + index + 1
        prior_ref_year = prior_ref[:4]

        if prior_ref_year.isnumeric() and int(prior_ref_year) < 2022:
            # Skip validation for pre-UEI prior references
            continue
        elif prior_ref not in previous_findings:
            # Error if we can't find the prior finding in previous
            errors.append(
                {
                    "error": err_prior_ref_not_found(
                        auditee_uei, prior_ref, award_ref, current_row
                    ),
                }
            )


def _validate_prior_refs(
    prior_refs, award_ref, auditee_uei, previous_report_ids, errors
):
    """
    Performs validation on the given list of prior reference numbers
    """
    first_row = FINDINGS_TEMPLATE["title_row"]

    for index, prior_ref in enumerate(prior_refs):
        current_row = first_row + index + 1
        prior_ref_year = prior_ref[:4]

        if prior_ref_year.isnumeric() and int(prior_ref_year) < 2022:
            # Skip validation for pre-UEI prior references
            continue
        elif not previous_report_ids:
            errors.append(
                {
                    "error": err_prior_ref_not_found(
                        auditee_uei, prior_ref, award_ref, current_row
                    ),
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
                    "error": err_prior_ref_not_found(
                        auditee_uei, prior_ref, award_ref, current_row
                    ),
                }
            )


def _compare_errors(audit_errors, errors):
    if audit_errors != errors:
        logger.error(
            f"<SOT ERROR> Finding Prior References Error: {audit_errors} Audit: {errors}"
        )
