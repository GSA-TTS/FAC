import logging

from django.views import generic
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from audit.mixins import (
    CertifyingAuditeeRequiredMixin,
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import Audit
from audit.models.constants import STATUS, EventType

from audit.models.viewflow import audit_transition
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
            audit = Audit.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": audit.submission_status,
            }
            return render(
                request, "audit/cross-validation/ready-for-certification.html", context
            )
        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    @verify_status(STATUS.IN_PROGRESS)
    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            audit = Audit.objects.get(report_id=report_id)
            errors = audit.validate()

            if not errors:
                audit_transition(
                    request=request,
                    audit=audit,
                    event=EventType.LOCKED_FOR_CERTIFICATION,
                )
                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))
            else:
                context = {"report_id": report_id, "errors": errors}
                return render(
                    request,
                    "audit/cross-validation/cross-validation-results.html",
                    context,
                )

        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class CertificationView(CertifyingAuditeeRequiredMixin, generic.View):
    @verify_status(STATUS.AUDITOR_CERTIFIED)
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            audit = Audit.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": audit.submission_status,
            }

            return render(request, "audit/certification.html", context)
        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    @verify_status(STATUS.AUDITOR_CERTIFIED)
    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            audit = Audit.objects.get(report_id=report_id)
            audit.save()

            return redirect(reverse("audit:MySubmissions"))

        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
