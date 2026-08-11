from .errors import err_identical_resubmissions


def check_resubmission_has_changes(sac_dict, *_args, **_kwargs):
    """
    Errors if the SAC is a resubmission that has no changes compared to the
    previous version
    """
    from audit.viewlib import compare_two_submissions
    from audit.models import SingleAuditChecklist

    sf_sac_meta = sac_dict.get("sf_sac_meta", {})
    resub_meta = sf_sac_meta.get("resubmission_meta") or {}

    previous_report_id = resub_meta.get("previous_report_id")
    if not resub_meta.get("previous_report_id"):
        return []

    report_id = sf_sac_meta.get("report_id")

    try:
        resub = SingleAuditChecklist.objects.get(report_id=report_id)
    except SingleAuditChecklist.DoesNotExist:
        return []

    _, _, compared = compare_two_submissions.compare_with_prev(resub)
    has_diff = False

    for val in compared.values():
        if val == "error" or val["status"] == "error":
            return [{"error": val["message"]}]
        if val["status"] != "same":
            has_diff = True

    if not has_diff:
        return [{"error": err_identical_resubmissions(previous_report_id)}]
    else:
        return []
