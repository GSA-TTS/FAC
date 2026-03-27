from audit.check_resubmission_allowed import (
    check_resubmission_allowed,
)


def check_resubmission_still_allowed(sac_data, **kwargs):
    from audit.models import SingleAuditChecklist

    sf_sac_meta = sac_data.get("sf_sac_meta", {})
    current_report_id = sf_sac_meta.get("report_id")

    if not current_report_id:
        return []

    try:
        current_sac = SingleAuditChecklist.objects.get(report_id=current_report_id)
    except SingleAuditChecklist.DoesNotExist:
        return []

    current_resub_meta = current_sac.resubmission_meta or {}
    parent_report_id = current_resub_meta.get("previous_report_id")

    # Only applies to actual resubmissions
    if not parent_report_id:
        return []

    try:
        parent_sac = SingleAuditChecklist.objects.get(report_id=parent_report_id)
    except SingleAuditChecklist.DoesNotExist:
        return []

    allowed, _message = check_resubmission_allowed(parent_sac)

    if allowed:
        return []

    return [
        {
            "error": (
                "This audit is no longer eligible for resubmission. Another "
                "resubmission may already have been submitted. Please refresh "
                "and start from the most recent version."
            )
        }
    ]
