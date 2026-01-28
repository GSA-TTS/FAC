import logging

from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import SingleAuditChecklist, SubmissionEvent, Audit
from audit.forms import TribalAuditConsentForm
from audit.validators import validate_tribal_data_consent_json


logger = logging.getLogger(__name__)


class TribalDataConsent(SingleAuditChecklistAccessRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            # SOT TODO: This does not yet use `audit` at all, and
            # will need to be updated.
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            tribal_audit_consent = sac.tribal_data_consent or {}

            context = {
                "auditee_uei": sac.auditee_uei,
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
            }

            if sac.resubmission_meta:
                previous_sac = SingleAuditChecklist.objects.get(
                    report_id=sac.resubmission_meta["previous_report_id"]
                )
                # This arose accidentally via testing, but might be an actual case.
                # We assume the previous audit was tribal. What if it wasn't?
                # What if they submitted "incorrectly," and are resubmitting to set their status
                # to tribal, and then add consent. This would mean that the previous tribal_data_consent
                # field was NULL in the DB (or None).
                previous_consent = previous_sac.tribal_data_consent

                # If previous_consent is None, we should not build a banner. As a result, we'll set no context.
                # If there is a value, we'll use it to build the context we pass back to the frontend.
                if previous_consent is not None:
                    context = context | {
                        "previous_report_id": previous_sac.report_id,
                        # The .get() should always work here, because we determined that
                        # previous_consent is not None.
                        "previous_is_public": (
                            previous_consent.get(
                                "is_tribal_information_authorized_to_be_public"
                            )
                        ),
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
            # SOT TODO: This does not yet use `audit` at all, and
            # will need to be updated.
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

                # TODO: Update Post SOC Launch
                audit = Audit.objects.find_audit_or_none(report_id=report_id)
                if audit:
                    # audit = Audit.objects.get(report_id=report_id)
                    audit.audit.update({"tribal_data_consent": tribal_data_consent})
                    audit.save(
                        event_user=request.user,
                        event_type=SubmissionEvent.EventType.TRIBAL_CONSENT_UPDATED,
                    )

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
