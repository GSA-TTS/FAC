from audit.check_resubmission_allowed import (
    check_resubmission_allowed,
)


def check_resubmission_still_allowed(sac_data, **kwargs):
    from audit.models import SingleAuditChecklist

    sf_sac_meta = sac_data.get("sf_sac_meta", {})
    report_id = sf_sac_meta.get("report_id")

    if not report_id:
        return []

    try:
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
    except SingleAuditChecklist.DoesNotExist:
        return []

    # 🔥 KEY FIX: only run for resubmissions
    if not sac.resubmission_meta:
        return []

    allowed, _message = check_resubmission_allowed(sac)

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
