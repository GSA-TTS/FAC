import logging

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    SingleAuditChecklist,
    SubmissionEvent, Audit,
)
from audit.forms import TribalAuditConsentForm
from audit.validators import validate_tribal_data_consent_json


logger = logging.getLogger(__name__)


class TribalDataConsent(SingleAuditChecklistAccessRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            tribal_audit_consent = sac.tribal_data_consent or {}

            context = {
                "auditee_uei": sac.auditee_uei,
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
            }

            return render(
                request,
                "audit/tribal-data-release.html",
                context | tribal_audit_consent,
            )
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            form = TribalAuditConsentForm(request.POST or None)

            if form.is_valid():
                form.clean_booleans()
                tribal_data_consent = form.cleaned_data
                validated = validate_tribal_data_consent_json(tribal_data_consent)
                sac.tribal_data_consent = validated
                sac.save(
                    event_user=request.user,
                    event_type=SubmissionEvent.EventType.TRIBAL_CONSENT_UPDATED,
                )
                logger.info("Tribal data consent saved.", tribal_data_consent)

                # TODO: 2/25 access audit
                # remove try/except once we are ready to deprecate SAC.
                try:
                    audit = Audit.objects.get(report_id=report_id)
                    audit.audit.update({"tribal_data_consent": tribal_data_consent})
                    audit.save(
                        event_user=request.user,
                        event_type=SubmissionEvent.EventType.TRIBAL_CONSENT_UPDATED,
                    )
                except Audit.DoesNotExist:
                    pass

                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

            tribal_data_consent = sac.tribal_data_consent or {}

            context = {
                "auditee_uei": sac.auditee_uei,
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "errors": form.errors,
            }

            return render(
                request,
                "audit/tribal-data-release.html",
                context | tribal_data_consent,
            )

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
