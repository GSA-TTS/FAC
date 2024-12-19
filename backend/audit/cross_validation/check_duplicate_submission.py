from datetime import datetime

from dissemination.models import General
from .errors import err_duplicate_submission


def check_duplicate_submission(sac_dict, *_args, **_kwargs):
    """
    Check that there isn't already a submission for this UEI and audit year.
    If a duplicate is allowed by an admin, this is a legitimate resbmission and does not throw an error.
    """
    all_sections = sac_dict["sf_sac_sections"]
    general_information = all_sections.get("general_information", {})
    
    fiscal_period_start = general_information.get("auditee_fiscal_period_start")

    audit_year = datetime.strptime(fiscal_period_start, "%Y-%m-%d").year
    uei = general_information.get("auditee_uei")

    if not (audit_year and uei):
        return []

    # check disseminated.
    is_duplicate =  General.objects.filter(
        audit_year=audit_year, auditee_uei=uei
    )

    # Check for admin permission. Loop through duplicates and ensure there is admin permission for each report_id
    # Or just check the latest duplicate for permission, to try and prevent double-firing a resubmission
    # duplicates_report_ids = General.objects.filter(audit_year=audit_year, auditee_uei=uei).values("report_id")

    if is_duplicate:  # and there's no waiver
        return [{"error": err_duplicate_submission()}]
    else:
        return []
