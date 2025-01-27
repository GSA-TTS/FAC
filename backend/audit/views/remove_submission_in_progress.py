import logging
from django.shortcuts import redirect, render, reverse
from django.views import generic
from django.core.exceptions import PermissionDenied

from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    Access,
    SingleAuditChecklist,
)
from audit.views.views import verify_status
from audit.models.models import STATUS
from audit.models.viewflow import SingleAuditChecklistFlow
from audit.models.submission_event import SubmissionEvent
from audit.models.access_roles import ACCESS_ROLES

logger = logging.getLogger(__name__)


class RemoveSubmissionView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    """
    View for removing an audit.
    """

    template = "audit/remove-submission-in-progress.html"

    @verify_status(
        [
            STATUS.IN_PROGRESS,
            STATUS.READY_FOR_CERTIFICATION,
            STATUS.AUDITOR_CERTIFIED,
            STATUS.AUDITEE_CERTIFIED,
            STATUS.CERTIFIED,
        ]
    )
    def get(self, request, *args, **kwargs):
        """
        Show the audit to be removed and confirmation form.
        """
        report_id = kwargs["report_id"]
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        role_values = [role[0] for role in ACCESS_ROLES]
        if not Access.objects.filter(
            email=request.user.email, sac=sac, role__in=role_values
        ).exists():
            raise PermissionDenied("Only authorized auditors can remove audits.")

        context = {
            "auditee_uei": sac.general_information["auditee_uei"],
            "auditee_name": sac.general_information.get("auditee_name"),
            "report_id": sac.report_id,
            "fiscal_year_end_date": sac.general_information.get(
                "auditee_fiscal_period_end"
            ),
        }

        return render(request, self.template, context)

    @verify_status(
        [
            STATUS.IN_PROGRESS,
            STATUS.READY_FOR_CERTIFICATION,
            STATUS.AUDITOR_CERTIFIED,
            STATUS.AUDITEE_CERTIFIED,
            STATUS.CERTIFIED,
        ]
    )
    def post(self, request, *args, **kwargs):
        """
        Remove the audit and redirect to the audits list.
        """
        report_id = kwargs["report_id"]
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        role_values = [role[0] for role in ACCESS_ROLES]
        if not Access.objects.filter(
            email=request.user.email, sac=sac, role__in=role_values
        ).exists():
            raise PermissionDenied("Only authorized auditors can remove audits.")

        flow = SingleAuditChecklistFlow(sac)
        flow.transition_to_flagged_for_removal()
        sac.save(
            event_user=request.user,
            event_type=SubmissionEvent.EventType.FLAGGED_SUBMISSION_FOR_REMOVAL,
        )
        url = reverse("audit:MySubmissions")

        return redirect(url)
