from datetime import datetime

from dissemination.models import General
from .errors import err_duplicate_submission


def check_duplicate_submission(sac_dict, *_args, **_kwargs):
    """
    Check that there isn't already a submission for this UEI and audit year.
    If a duplicate is allowed by an admin, this is a legitimate resbmission and does not throw an error.
    """
    # Importing here to avoid circular import
    from audit.models import is_resubmission

    all_sections = sac_dict["sf_sac_sections"]
    general_information = all_sections.get("general_information", {})

    fiscal_period_start = general_information.get("auditee_fiscal_period_start")
    uei = general_information.get("auditee_uei")

    if not (fiscal_period_start and uei):
        return []

    audit_year = datetime.strptime(fiscal_period_start, "%Y-%m-%d").year

    # Check for a waiver
    if not is_resubmission(uei, audit_year):
        return []

    # Check disseminated for a duplicate
    duplicates = General.objects.filter(audit_year=audit_year, auditee_uei=uei)

    if duplicates:
        return [{"error": err_duplicate_submission()}]

    return []
