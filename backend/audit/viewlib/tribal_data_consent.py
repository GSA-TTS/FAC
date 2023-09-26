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

                sac.tribal_data_consent = form.cleaned_data
                sac.save(
                    event_user=request.user,
                    event_type=SubmissionEvent.EventType.TRIBAL_CONSENT_UPDATED,
                )

                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

            tribal_audit_consent = sac.tribal_data_consent or {}

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
