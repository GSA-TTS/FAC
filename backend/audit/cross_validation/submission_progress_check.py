from audit.cross_validation.naming import NC, find_section_by_name
from audit.models.submission_event import SubmissionEvent
from audit.validators import validate_general_information_complete_json
from django.core.exceptions import ValidationError


def submission_progress_check(sac, sar=None, crossval=True):
    """
    Because this function was initially created in a view and not as a
    cross-validation function, it needs the crossval argument to distinguish between
    running in a cross-validation context and running in the context of needing to
    return progress information to the submission progress view.

    crossval defaults to True because we don't want to have to change all the calls to
    the validation functions to include this argument.

    Given the output of sac_validation_shape on a SingleAuditChecklist instance, and
    a SingleAuditReportFile instance, return information about submission progress.

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
            "section_sname": [snake_case name of section],
            "display": "inactive"/"incomplete"/"complete",
            "completed": [bool],
            "completed_by": [email],
            "completed_date": [date],
        }
    """

    # Add the status of the SAR into the list of sections:
    sac["sf_sac_sections"][NC.SINGLE_AUDIT_REPORT] = bool(sar)

    result = {k: None for k in sac["sf_sac_sections"]}

    for key in sac["sf_sac_sections"]:
        result = result | progress_check(sac, sac["sf_sac_sections"], key)

    incomplete_sections = []
    for k in result:
        if result[k].get("display") == "incomplete":
            incomplete_sections.append(find_section_by_name(k).friendly)

    result["complete"] = len(incomplete_sections) == 0

    if not crossval:
        return result  # return the submission progress shape.

    if result["complete"]:
        return []

    return [
        {
            "error": f"The following sections are incomplete: {', '.join(incomplete_sections)}."
        }
    ]


def progress_check(sac, sections, key):
    """
    Given the content of sf_sac_sections from sac_validation_shape (plus a
    single_audit_report key) and a key, determine whether that key is required, and
    return a dictionary containing that key with its progress as the value.
    """

    def get_num_findings(award):
        if program := award.get("program"):
            if findings := program.get("number_of_audit_findings", 0):
                return int(findings)
        return 0

    progress = {
        "display": None,
        "completed": None,
        "completed_by": None,
        "completed_date": None,
        "section_name": key,
    }
    awards = {}
    if sections[NC.FEDERAL_AWARDS]:
        awards = sections.get(NC.FEDERAL_AWARDS, {}).get(NC.FEDERAL_AWARDS, [])
    general_info = sections.get(NC.GENERAL_INFORMATION, {}) or {}

    num_findings = sum(get_num_findings(award) for award in awards)
    conditions = {
        NC.GENERAL_INFORMATION: True,
        NC.AUDIT_INFORMATION: True,
        NC.FEDERAL_AWARDS: True,
        NC.NOTES_TO_SEFA: True,
        NC.FINDINGS_UNIFORM_GUIDANCE: num_findings > 0,
        NC.FINDINGS_TEXT: num_findings > 0,
        NC.CORRECTIVE_ACTION_PLAN: num_findings > 0,
        NC.ADDITIONAL_UEIS: bool(general_info.get("multiple_ueis_covered")),
        NC.ADDITIONAL_EINS: bool(general_info.get("multiple_eins_covered")),
        NC.SECONDARY_AUDITORS: bool(general_info.get("secondary_auditors_exist")),
        NC.SINGLE_AUDIT_REPORT: True,
        NC.TRIBAL_DATA_CONSENT: bool(
            general_info.get("user_provided_organization_type") == "tribal"
        ),
    }

    # The General Information has its own condition, as it can be partially completed.
    if key == "general_information":
        return general_information_progress_check(progress, general_info, sac)

    # If it's not required, it's inactive:
    if not conditions[key]:
        return {key: progress | {"display": "inactive"}}

    # If it is required, it should be present
    if sections.get(key):
        completed_by, completed_date = section_completed_metadata(sac, key)

        return {
            key: progress
            | {
                "display": "complete",
                "completed": True,
                "completed_by": completed_by,
                "completed_date": completed_date,
            }
        }

    return {key: progress | {"display": "incomplete", "completed": False}}


def section_completed_metadata(sac, section_key):
    try:
        section = find_section_by_name(section_key)
        event_type = section.submission_event

        report_id = sac["sf_sac_meta"]["report_id"]
        event = SubmissionEvent.objects.filter(
            sac__report_id=report_id, event=event_type
        ).latest("timestamp")

        return event.user.email, event.timestamp
    except SubmissionEvent.DoesNotExist:
        return None, None


def general_information_progress_check(progress, general_info, sac):
    """
    Given a base "progress" dictionary and the general_info object from a submission,
    run validations to determine its completeness. Then, return a dictionary with
    "general_information" as the key and the progress as the value.
    """
    try:
        is_general_info_complete = bool(
            validate_general_information_complete_json(general_info)
        )
    except ValidationError:
        is_general_info_complete = False

    if is_general_info_complete:
        completed_by, completed_date = section_completed_metadata(
            sac, "general_information"
        )

        return {
            "general_information": progress
            | {
                "display": "complete",
                "completed": True,
                "completed_by": completed_by,
                "completed_date": completed_date,
            }
        }
    return {
        "general_information": progress | {"display": "incomplete", "completed": False}
    }
