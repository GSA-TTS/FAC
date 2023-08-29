from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views import generic
from audit.cross_validation import (
    naming,
    sac_validation_shape,
    submission_progress_check,
)
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    SingleAuditChecklist,
    SingleAuditReportFile,
)


# Turn the named tuples into dicts because Django templates work with dicts:
SECTIONS_NAMING = {k: v._asdict() for k, v in naming.SECTION_NAMES.items()}

# The info for the submission page sections:
SECTIONS_PAGE = {
    "general_information": {
        "edit_text": f"Edit the {SECTIONS_NAMING['general_information']['friendly_title']}",
        "text": "Enter general information about the single audit submission, such as the audit type and fiscal period. This is also where you'll list the primary auditor and auditee contacts.",
    },
    "audit_information": {
        "edit_text": f"Edit the {SECTIONS_NAMING['audit_information']['friendly_title']}",
        "text": "Select the status of the financial statements and federal programs covered by your single audit.",
    },
    "single_audit_report": {
        "edit_text": f"Edit the {SECTIONS_NAMING['single_audit_report']['friendly_title']}",
        "text": "Upload the audit report. This should be a single PDF that is unlocked and machine-readable.",
    },
    "federal_awards": {
        "edit_text": f"Edit the {SECTIONS_NAMING['federal_awards']['friendly_title']}",
        "text": "For each federal award received, you'll need the financial and agency details. This is also where you list the number of audit findings.",
        "text_nb": "You must complete this workbook first.",
    },
    "notes_to_sefa": {
        "edit_text": f"Edit the {SECTIONS_NAMING['notes_to_sefa']['friendly_title']}",
        "text": "This workbook covers notes on the Schedule of Expenditures of Federal Awards (SEFA). Enter the information of each Federal awards program from which the auditee received funds, even if they don't have audit findings.",
    },
    "findings_uniform_guidance": {
        "edit_text": f"Edit the {SECTIONS_NAMING['findings_uniform_guidance']['friendly_title']}",
        "text": "Complete this workbook using the Summary Schedule of Prior Audit Findings and the information in the financial statement audit. If there are no audit findings listed in Workbook 1: Federal Awards, only enter the auditee EIN in this workbook and upload.",
    },
    "findings_text": {
        "edit_text": f"Edit the {SECTIONS_NAMING['findings_text']['friendly_title']}",
        "text": "Enter the full text of the audit finding, listing each finding only once, even if they relate to more than one program. Include the audit finding reference number for each. If there are no audit findings listed in Workbook 1: Federal Awards, only enter the auditee EIN in this workbook and upload.",
    },
    "corrective_action_plan": {
        "edit_text": f"Edit the {SECTIONS_NAMING['corrective_action_plan']['friendly_title']}",
        "text": "This information should match the data you entered in the Findings Text workbook. You only need to enter plans for findings once if they relate to more than one program. If there are no audit findings listed in Workbook 1: Federal Awards, only enter the auditee EIN in this workbook and upload.",
    },
    "additional_ueis": {
        "edit_text": f"Edit the {SECTIONS_NAMING['additional_ueis']['friendly_title']}",
        "text": "This workbook is only necessary if the audit report covers multiple UEIs. List the additional UEIs covered by the audit, excluding the primary UEI.",
    },
    "secondary_auditors": {
        "edit_text": f"Edit the {SECTIONS_NAMING['secondary_auditors']['friendly_title']}",
        "text": "This workbook is only necessary if multiple auditors did the audit work.",
    },
    "additional_eins": {
        "edit_text": f"Edit the {SECTIONS_NAMING['additional_eins']['friendly_title']}",
        "text": "This workbook is only necessary if the audit report covers multiple EINs. List the additional EINs covered by the audit, excluding the primary EIN.",
    },
}

# Combine the submission page info with the naming info:
SECTIONS_BASE = {
    k: v | SECTIONS_PAGE[k] for k, v in SECTIONS_NAMING.items() if k in SECTIONS_PAGE
}


class SubmissionProgressView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    """
    Display information about and the current status of the sections of the submission,
    including links to the pages for the sections.

    The following sections have three states, rather than two:

    incomplete
    +   Findings Uniform Guidance
    +   Findings Text
    +   Corrective Action Plan
    +   Additionai UEIs
    +   Additionai EINs
    +   Secondary Auditors

    The states are:

    +   hidden
    +   incomplete
    +   complete

    In each case, they are hidden if the corresponding question in the General
    Information form has been answered with a negative response.
    """

    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            try:
                sar = SingleAuditReportFile.objects.filter(sac_id=sac.id).latest(
                    "date_created"
                )
            except SingleAuditReportFile.DoesNotExist:
                sar = None

            shaped_sac = sac_validation_shape(sac)
            subcheck = submission_progress_check(shaped_sac, sar, crossval=False)
            # Update with the view-specific info from SECTIONS_BASE:
            for key, value in SECTIONS_BASE.items():
                subcheck[key] = subcheck[key] | value

            context = {
                "single_audit_checklist": {
                    "created": True,
                    "created_date": sac.date_created,
                    "created_by": sac.submitted_by,
                    "completed": False,
                    "completed_date": None,
                    "completed_by": None,
                },
                "pre_submission_validation": {
                    "completed": sac.submission_status == "ready_for_certification",
                    "completed_date": None,
                    "completed_by": None,
                    # We want the user to always be able to run this check:
                    "enabled": True,
                },
                "certification": {
                    "auditor_certified": bool(sac.auditor_certification),
                    "auditor_enabled": sac.submission_status
                    == "ready_for_certification",
                    "auditee_certified": bool(sac.auditee_certification),
                    "auditee_enabled": sac.submission_status == "auditor_certified",
                },
                "submission": {
                    "completed": sac.submission_status == "submitted",
                    "completed_date": None,
                    "completed_by": None,
                    "enabled": sac.submission_status == "auditee_certified",
                },
                "report_id": report_id,
                "auditee_name": sac.auditee_name,
                "auditee_uei": sac.auditee_uei,
                "user_provided_organization_type": sac.user_provided_organization_type,
            }
            context = context | subcheck

            return render(
                request, "audit/submission_checklist/submission-checklist.html", context
            )
        except SingleAuditChecklist.DoesNotExist as err:
            raise PermissionDenied("You do not have access to this audit.") from err
