import logging

from django.views import generic
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from audit.forms import (
    AuditeeCertificationStep1Form,
    AuditeeCertificationStep2Form,
)
from audit.mixins import CertifyingAuditeeRequiredMixin

from audit.models import Audit
from audit.models.constants import STATUS, EventType

from audit.models.viewflow import audit_transition
from audit.validators import (
    validate_auditee_certification_json,
)
from audit.decorators import verify_status

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)


class AuditeeCertificationStep1View(CertifyingAuditeeRequiredMixin, generic.View):
    @verify_status(STATUS.AUDITOR_CERTIFIED)
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            audit = Audit.objects.get(report_id=report_id)
            initial = {
                "AuditeeCertificationStep1Session": request.session.get(
                    "AuditeeCertificationStep1Session", None
                )
            }
            form = AuditeeCertificationStep1Form(request.POST or None, initial=initial)
            context = {
                "auditee_uei": audit.auditee_uei,
                "auditee_name": audit.auditee_name,
                "report_id": report_id,
                "submission_status": audit.submission_status,
                "form": form,
            }

            return render(request, "audit/auditee-certification-step-1.html", context)

        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    @verify_status(STATUS.AUDITOR_CERTIFIED)
    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            audit = Audit.objects.get(report_id=report_id)
            initial = {
                "AuditeeCertificationStep1Session": request.session.get(
                    "AuditeeCertificationStep1Session", None
                )
            }
            form = AuditeeCertificationStep1Form(request.POST or None, initial=initial)
            context = {
                "auditee_uei": audit.auditee_uei,
                "auditee_name": audit.auditee_name,
                "report_id": report_id,
                "submission_status": audit.submission_status,
            }

            if form.is_valid():
                # Save to session. Retrieved and saved after step 2.
                request.session["AuditeeCertificationStep1Session"] = form.cleaned_data
                return redirect(
                    reverse("audit:AuditeeCertificationConfirm", args=[report_id])
                )

            context["form"] = form
            return render(request, "audit/auditee-certification-step-1.html", context)

        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class AuditeeCertificationStep2View(CertifyingAuditeeRequiredMixin, generic.View):
    @verify_status(STATUS.AUDITOR_CERTIFIED)
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            audit = Audit.objects.get(report_id=report_id)
            initial = {
                "AuditeeCertificationStep2Session": request.session.get(
                    "AuditeeCertificationStep2Session", None
                )
            }
            form = AuditeeCertificationStep2Form(request.POST or None, initial=initial)

            # Suggests a load/reload on step 2, which means we don't have step 1 session information.
            # Send them back.
            form1_cleaned = request.session.get(
                "AuditeeCertificationStep1Session", None
            )
            if form1_cleaned is None:
                return redirect(reverse("audit:AuditeeCertification", args=[report_id]))

            context = {
                "auditee_uei": audit.auditee_uei,
                "auditee_name": audit.auditee_name,
                "report_id": report_id,
                "submission_status": audit.submission_status,
                "form": form,
            }

            return render(request, "audit/auditee-certification-step-2.html", context)

        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    @verify_status(STATUS.AUDITOR_CERTIFIED)
    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            audit = Audit.objects.get(report_id=report_id)
            form1_cleaned = request.session.get(
                "AuditeeCertificationStep1Session", None
            )
            form2 = AuditeeCertificationStep2Form(request.POST or None)
            context = {
                "auditee_uei": audit.auditee_uei,
                "auditee_name": audit.auditee_name,
                "report_id": report_id,
                "submission_status": audit.submission_status,
            }

            if form2.is_valid():
                form_cleaned = {
                    "auditee_certification": form1_cleaned,
                    "auditee_signature": form2.cleaned_data,
                }
                form_cleaned["auditee_signature"][
                    "auditee_certification_date_signed"
                ] = form_cleaned["auditee_signature"][
                    "auditee_certification_date_signed"
                ].strftime(
                    "%Y-%m-%d"
                )
                auditee_certification = audit.audit.get("auditee_certification", {})
                auditee_certification.update(form_cleaned)
                validated = validate_auditee_certification_json(auditee_certification)

                audit.audit.update({"auditee_certification": validated})
                if audit_transition(
                    request=request,
                    audit=audit,
                    event=EventType.AUDITEE_CERTIFICATION_COMPLETED,
                ):
                    logger.info("Auditee certification saved.", auditee_certification)
                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

            context["form"] = form2
            return render(request, "audit/auditee-certification-step-2.html", context)

        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
