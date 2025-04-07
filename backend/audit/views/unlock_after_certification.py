import logging

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse

from audit.forms import UnlockAfterCertificationForm
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import Audit
from audit.models.constants import STATUS, EventType

from audit.models.viewflow import audit_transition
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
            sac = Audit.objects.get(report_id=report_id)
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
        except Audit.DoesNotExist:
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
            audit = Audit.objects.get(report_id=report_id)
            form = UnlockAfterCertificationForm(request.POST or None)
            acceptable = ("True", True)
            should_go_to_in_progress = (
                form.data.get("unlock_after_certification") in acceptable
            )

            if form.is_valid() and should_go_to_in_progress:
                if audit_transition(
                    request=request,
                    audit=audit,
                    transition_to=EventType.UNLOCKED_AFTER_CERTIFICATION,
                ):
                    logger.info("Submission unlocked after certification")

                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

            context = {
                "auditee_uei": audit.auditee_uei,
                "auditee_name": audit.auditee_name,
                "report_id": report_id,
                "errors": form.errors,
            }

            return render(
                request,
                "audit/unlock-after-certification.html",
                context,
            )

        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
