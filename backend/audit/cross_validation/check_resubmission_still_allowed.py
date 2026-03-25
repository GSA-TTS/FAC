from audit.check_resubmission_allowed import (
    check_resubmission_allowed,
)


def check_resubmission_still_allowed(sac_data, **kwargs):
    """
    Confirm that the current SAC is still eligible to be submitted as a
    resubmission.

    This is a user-facing validation meant to catch cases where another
    resubmission may already have been submitted for the same parent record.
    The database constraints still remain the final safety net.

    Returns:
        [] when the SAC is still eligible
        [{"error": "<message>"}] when the SAC is no longer eligible
    """
    from audit.models import SingleAuditChecklist

    sf_sac_meta = sac_data.get("sf_sac_meta", {})
    report_id = sf_sac_meta.get("report_id")

    if not report_id:
        return [
            {
                "error": (
                    "Unable to validate whether this resubmission is still "
                    "allowed because the report ID is missing."
                )
            }
        ]

    try:
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
    except SingleAuditChecklist.DoesNotExist:
        return [
            {
                "error": (
                    "Unable to validate whether this resubmission is still "
                    "allowed because the audit record could not be found."
                )
            }
        ]

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
