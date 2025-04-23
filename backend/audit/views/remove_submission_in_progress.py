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
    Audit,
)
from audit.models.constants import STATUS
from audit.models.viewflow import SingleAuditChecklistFlow, AuditFlow
from audit.models.submission_event import SubmissionEvent
from audit.models.access_roles import ACCESS_ROLES
from audit.decorators import verify_status

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
        self._remove_audit(report_id, request.user)

        url = reverse("audit:MySubmissions")

        return redirect(url)

    # TODO: Update Post SOC Launch : This can be merged into post above
    @staticmethod
    def _remove_audit(report_id, user):
        audit = Audit.objects.find_audit_or_none(report_id=report_id)
        if audit:
            flow = AuditFlow(audit=audit)
            flow.transition_to_flagged_for_removal()
            audit.save(
                event_user=user,
                event_type=SubmissionEvent.EventType.FLAGGED_SUBMISSION_FOR_REMOVAL,
            )
