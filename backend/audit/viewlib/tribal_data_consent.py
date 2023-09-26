from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    SingleAuditChecklist,
    SubmissionEvent,
)
from audit.forms import TribalAuditConsentForm

from datetime import datetime


class TribalDataConsent(SingleAuditChecklistAccessRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            tribal_audit_consent = sac.tribal_data_consent or {}
            if tribal_audit_consent.get(
                "tribal_authorization_certifying_official_date"
            ):
                tribal_audit_consent[
                    "tribal_authorization_certifying_official_date"
                ] = datetime.strptime(
                    tribal_audit_consent[
                        "tribal_authorization_certifying_official_date"
                    ],
                    "%Y-%m-%d",
                ).strftime(
                    "%Y-%m-%d"
                )

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
                cleaned_data = form.cleaned_data
                cleaned_data[
                    "tribal_authorization_certifying_official_date"
                ] = cleaned_data[
                    "tribal_authorization_certifying_official_date"
                ].strftime(
                    "%Y-%m-%d"
                )
                sac.tribal_data_consent = cleaned_data
                sac.save(
                    event_user=request.user,
                    event_type=SubmissionEvent.EventType.TRIBAL_CONSENT_UPDATED,
                )

                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

            tribal_audit_consent = sac.get("tribal_data_consent")

            context = {
                "auditee_uei": sac.auditee_uei,
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "errors": form.errors,
            }

            return render(
                request,
                "audit/tribal-data-release.html",
                context | tribal_audit_consent,
            )

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
