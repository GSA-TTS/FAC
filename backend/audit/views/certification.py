import logging

from django.views import generic
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from audit.mixins import (
    CertifyingAuditeeRequiredMixin,
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    SingleAuditChecklist,
    Audit,
)
from audit.models.models import STATUS
from audit.models.viewflow import sac_transition
from audit.decorators import verify_status


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)


class ReadyForCertificationView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    @verify_status(STATUS.IN_PROGRESS)
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }
            return render(
                request, "audit/cross-validation/ready-for-certification.html", context
            )
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    @verify_status(STATUS.IN_PROGRESS)
    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            # TODO: Update Post SOC Launch
            # remove try/except once we are ready to deprecate SAC.
            audit = Audit.objects.find_audit_or_none(report_id=report_id)
            errors = sac.validate_full()
            if not errors:
                sac_transition(
                    request,
                    sac,
                    audit=audit,
                    transition_to=STATUS.READY_FOR_CERTIFICATION,
                )
                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))
            else:
                context = {"report_id": report_id, "errors": errors}
                return render(
                    request,
                    "audit/cross-validation/cross-validation-results.html",
                    context,
                )

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class CertificationView(CertifyingAuditeeRequiredMixin, generic.View):
    @verify_status(STATUS.AUDITOR_CERTIFIED)
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }

            return render(request, "audit/certification.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    @verify_status(STATUS.AUDITOR_CERTIFIED)
    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            sac.save()

            return redirect(reverse("audit:MySubmissions"))

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
