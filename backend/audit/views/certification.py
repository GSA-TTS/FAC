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
from audit.models.constants import STATUS
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
            audit = Audit.objects.find_audit_or_none(report_id=report_id)
            errors = sac.validate_full()

            if audit:
                audit_errors = audit.validate()
                _compare_errors(errors, audit_errors)

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


# TODO: Post SOT Launch: Delete
def _compare_errors(sac_errors, audit_errors):
    sac = sac_errors.copy() if sac_errors else dict({"data": {}})
    audit = audit_errors.copy() if audit_errors else dict({"data": {}})

    sac_metadata = sac.get("data", {}).get("sf_sac_meta", {})
    audit_metadata = audit.get("data", {}).get("sf_sac_meta", {})

    remove_fields = ("date_created", "transition_name", "transition_date")
    for field in remove_fields:
        if field in sac_metadata:
            del sac_metadata[field]
        if field in audit_metadata:
            del audit_metadata[field]

    sac["data"]["sf_sac_meta"] = sac_metadata
    audit["data"]["sf_sac_meta"] = audit_metadata
    if (sac and not audit) or (audit and not sac) or (sac != audit):
        logger.error(
            f"<SOT ERROR> Certification Errors do not match: SAC {sac_errors}, Audit {audit_errors}"
        )
