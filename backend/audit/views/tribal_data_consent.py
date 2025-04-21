import logging

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import Audit
from audit.forms import TribalAuditConsentForm
from audit.models.constants import EventType
from audit.validators import validate_tribal_data_consent_json


logger = logging.getLogger(__name__)


class TribalDataConsent(SingleAuditChecklistAccessRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            audit = Audit.objects.get(report_id=report_id)
            tribal_audit_consent = audit.audit.get("tribal_data_consent", {})

            context = {
                "auditee_uei": audit.auditee_uei,
                "auditee_name": audit.auditee_name,
                "report_id": report_id,
            }

            return render(
                request,
                "audit/tribal-data-release.html",
                context | tribal_audit_consent,
            )
        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            audit = Audit.objects.get(report_id=report_id)
            form = TribalAuditConsentForm(request.POST or None)

            if form.is_valid():
                form.clean_booleans()
                tribal_data_consent = form.cleaned_data
                validated = validate_tribal_data_consent_json(tribal_data_consent)

                audit.audit.update({"tribal_data_consent": validated})
                audit.save(
                    event_user=request.user,
                    event_type=EventType.TRIBAL_CONSENT_UPDATED,
                )
                logger.info("Tribal data consent saved.", tribal_data_consent)

                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

            tribal_data_consent = audit.audit.get("tribal_data_consent", {})

            context = {
                "auditee_uei": audit.auditee_uei,
                "auditee_name": audit.auditee_name,
                "report_id": report_id,
                "errors": form.errors,
            }

            return render(
                request,
                "audit/tribal-data-release.html",
                context | tribal_data_consent,
            )

        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
