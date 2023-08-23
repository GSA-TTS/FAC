from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views import generic
from audit.cross_validation import sac_validation_shape, submission_progress_check
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    SingleAuditChecklist,
    SingleAuditReportFile,
)


class SubmissionProgressView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    """
    Display information about and the current status of the sections of the submission,
    including links to the pages for the sections.

    The following sections have three states, rather than two:

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
