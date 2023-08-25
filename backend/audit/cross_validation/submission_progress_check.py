def submission_progress_check(sac, sar=None, crossval=True):
    """
    Because this function was initially created in a view and not as a
    cross-validation function, it needs the crossval argument to distinguish between
    running in a cross-validation context and running in the context of needing to
    return progress information to the submission progress view.

    crossval defaults to True because we don't want to have to change all the calls to
    the validation functions to include this argument.

    Given a SingleAuditChecklist instance and a SingleAuditReportFile instance,
    return information about submission progress.

    Returns this shape:

        {
            "complete": [bool],
            "single_audit_report": [progress_dict],
            "additional_ueis": [progress_dict],
            ...
            "general_information": [progress_dict],
        }

    Where each of the sections is represented at the top level, along with
    single_audit_report, and [progress_dict] is:

        {
            "display": "hidden"/"incomplete"/"complete",
            "completed": [bool],
            "completed_by": [email],
            "completed_date": [date],
        }
    """
    sections = sac["sf_sac_sections"]
    # TODO: remove these once tribal data consent are implemented
    del sections["tribal_data_consent"]
    result = {k: None for k in sections}  # type: ignore
    progress = {
        "display": None,
        "completed": None,
        "completed_by": None,
        "completed_date": None,
    }

    cond_keys = _conditional_keys_progress_check(sections)
    for ckey, cvalue in cond_keys.items():
        result[ckey] = progress | cvalue

    mandatory_keys = _mandatory_keys_progress_check(sections, cond_keys)
    for mkey, mvalue in mandatory_keys.items():
        result[mkey] = progress | mvalue

    sar_progress = {
        "display": "complete" if bool(sar) else "incomplete",
        "completed": bool(sar),
    }

    result["single_audit_report"] = progress | sar_progress  # type: ignore

    complete = False

    def cond_pass(cond_key):
        passing = ("hidden", "complete")
        return result.get(cond_key, {}).get("display") in passing

    error_keys = (
        list(mandatory_keys.keys()) + list(cond_keys.keys()) + ["single_audit_report"]
    )

    # Need this to return useful errors in cross-validation:
    incomplete_sections = [
        k for k in error_keys if result[k].get("display") == "incomplete"
    ]

    if all(bool(sections[k]) for k in mandatory_keys):
        if all(cond_pass(j) for j in cond_keys):
            complete = True

    result["complete"] = complete  # type: ignore

    if not crossval:
        return result  # return the cross-validation shape

    if complete:
        return []

    return [
        {
            "error": f"The following sections are incomplete: {', '.join(incomplete_sections)}."
        }
    ]


def _conditional_keys_progress_check(sections):
    """
    Support function for submission_progress_check; handles the conditional sections.
    """
    general_info = sections.get("general_information") or {}
    conditional_keys = {
        "additional_ueis": general_info.get("multiple_ueis_covered"),
        # Update once we have the question in. This may be handled in the gen info form rather than as a workbook.
        "additional_eins": general_info.get("multiple_eins_covered"),
        "secondary_auditors": general_info.get(
            "secondary_auditors_exist"
        ),  # update this once we have the question in.
    }
    output = {}
    for key, value in conditional_keys.items():
        current = "incomplete"
        if not value:
            current = "hidden"
        elif sections.get(key):
            current = "complete"
        info = {"display": current, "completed": current == "complete"}
        output[key] = info
    return output


def _mandatory_keys_progress_check(sections, conditional_keys):
    """
    Support function for submission_progress_check; handles the mandatory sections.
    """
    other_keys = [k for k in sections if k not in conditional_keys]
    output = {}
    for k in other_keys:
        if bool(sections[k]):
            info = {"display": "complete", "completed": True}
        else:
            info = {"display": "incomplete", "completed": False}
        output[k] = info
    return output
