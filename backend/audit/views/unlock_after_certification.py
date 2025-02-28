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
    Audit,
)
from audit.models.models import STATUS
from audit.models.viewflow import sac_transition
from audit.decorators import verify_status


logger = logging.getLogger(__name__)


class UnlockAfterCertificationView(
    SingleAuditChecklistAccessRequiredMixin, generic.View
):
    """
    View to allow users to send a submission back to IN_PROGRESS from
    READY_FOR_CERTIFICATION.
    """

    @verify_status(
        [
            STATUS.READY_FOR_CERTIFICATION,
            STATUS.AUDITOR_CERTIFIED,
            STATUS.AUDITEE_CERTIFIED,
        ]
    )
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            target_statuses = [
                STATUS.READY_FOR_CERTIFICATION,
                STATUS.AUDITOR_CERTIFIED,
                STATUS.AUDITEE_CERTIFIED,
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

    @verify_status(
        [
            STATUS.READY_FOR_CERTIFICATION,
            STATUS.AUDITOR_CERTIFIED,
            STATUS.AUDITEE_CERTIFIED,
        ]
    )
    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            form = UnlockAfterCertificationForm(request.POST or None)
            acceptable = ("True", True)
            should_go_to_in_progress = (
                form.data.get("unlock_after_certification") in acceptable
            )
            audit = Audit.objects.find_audit_or_none(report_id=report_id)
            if form.is_valid() and should_go_to_in_progress:
                if sac_transition(
                    request, sac, audit=audit, transition_to=STATUS.IN_PROGRESS
                ):
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
