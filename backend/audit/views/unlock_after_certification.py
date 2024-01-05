import logging

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse
from audit.forms import UnlockAfterCertificationForm
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    SingleAuditChecklist,
    SubmissionEvent,
)

logger = logging.getLogger(__name__)


class UnlockAfterCertificationView(
    SingleAuditChecklistAccessRequiredMixin, generic.View
):
    """
    View to allow users to send a submission back to IN_PROGRESS from
    READY_FOR_CERTIFICATION.
    """

    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            target_statuses = [
                SingleAuditChecklist.STATUS.READY_FOR_CERTIFICATION,
                SingleAuditChecklist.STATUS.AUDITOR_CERTIFIED,
                SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED,
            ]
            context = {
                "auditee_uei": sac.auditee_uei,
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "submission_status": sac.submission_status,
                "target_statuses": target_statuses,
            }

            return render(
                request,
                "audit/unlock-after-certification.html",
                context,
            )
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            form = UnlockAfterCertificationForm(request.POST or None)
            acceptable = ("True", True)
            should_go_to_in_progress = (
                form.data.get("unlock_after_certification") in acceptable
            )
            if form.is_valid() and should_go_to_in_progress:
                sac.transition_to_in_progress_again()
                sac.save(
                    event_user=request.user,
                    event_type=SubmissionEvent.EventType.UNLOCKED_AFTER_CERTIFICATION,
                )
                logger.info("Submission unlocked after certification")

                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

            context = {
                "auditee_uei": sac.auditee_uei,
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "errors": form.errors,
            }

            return render(
                request,
                "audit/unlock-after-certification.html",
                context,
            )

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
