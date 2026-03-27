def check_parent_resubmission_conflict(sac_data, **kwargs):
    """
    Checks for conflicting resubmissions originating from the same parent record.

    Prevents race conditions where multiple resubmissions are created from the same
    parent audit, which would result in a branching resubmission chain.

    This is a user-facing validation. Database constraints remain the final safeguard.

    Returns:
        [] when no competing resubmission exists
        [{"error": "<message>"}] when a competing resubmission is found
    """
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

    sibling_candidates = SingleAuditChecklist.objects.exclude(
        report_id=current_report_id
    ).exclude(resubmission_meta__isnull=True)

    matching_siblings = [
        sac
        for sac in sibling_candidates
        if (sac.resubmission_meta or {}).get("previous_report_id") == parent_report_id
    ]

    if not matching_siblings:
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
