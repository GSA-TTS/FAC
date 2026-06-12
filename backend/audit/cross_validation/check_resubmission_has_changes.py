def check_resubmission_has_changes(sac_dict, *_args, **_kwargs):
    """
    Errors if the SAC is a resubmission that has no changes compared to the
    previous version
    """
    from audit.viewlib.compare_two_submissions import compare_with_prev
    from audit.models import SingleAuditChecklist

    sf_sac_meta = sac_dict.get("sf_sac_meta", {})
    resub_meta = sf_sac_meta.get("resubmission_meta") or {}

    if not resub_meta.get("previous_report_id"):
        return []

    report_id = sf_sac_meta.get("report_id")

    try:
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
    except SingleAuditChecklist.DoesNotExist:
        return []

    _, _, compared = compare_with_prev(sac)
    has_diff = False

    for val in compared.values():
        if val == "error" or val["status"] == "error":
            return [{"error": compared.message}]
        if val["status"] != "same":
            has_diff = True

    if not has_diff:
        return [{"error": f"This resubmission appears identical to the previous version ({report_id}). A resubmission that is identical to the original submission is not permitted."}]
    else:
        return []
