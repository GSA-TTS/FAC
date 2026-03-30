from audit.check_resubmission_allowed import (
    check_resubmission_allowed,
)


def check_resubmission_still_allowed(sac_data, **kwargs):
    from audit.models import SingleAuditChecklist

    sf_sac_meta = sac_data.get("sf_sac_meta", {})
    current_resub_meta = sf_sac_meta.get("resubmission_meta") or {}

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

    return [{"error": ("Only the most recent version may initiate resubmission.")}]
