import logging

from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View

from audit.formlib import ResubmissionActionForm
from audit.mixins import SingleAuditChecklistAccessRequiredMixin
from audit.models import (
    Audit,
    SingleAuditChecklist,
    SingleAuditReportFile,
    SubmissionEvent,
)
from audit.models.constants import RESUBMISSION_ACTION
from audit.views.upload_report_view import copy_previous_report_data

logger = logging.getLogger(__name__)


class ResubmissionActionEditView(SingleAuditChecklistAccessRequiredMixin, View):
    template_name = "audit/resubmission_action_edit.html"

    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        sac = SingleAuditChecklist.objects.get(report_id=report_id)

        meta = sac.resubmission_meta or {}

        form = ResubmissionActionForm(
            initial={
                "resubmission_action": meta.get("resubmission_action"),
                "resubmission_requester": meta.get("resubmission_requester", []),
                "material_change_reasons": meta.get("material_change_reasons", []),
                "non_material_change_reasons": meta.get(
                    "non_material_change_reasons", []
                ),
            }
        )

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "report_id": report_id,
            },
        )

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        form = ResubmissionActionForm(request.POST)

        # First, handle the form data.
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "form": form,
                    "report_id": report_id,
                },
            )

        sac.resubmission_meta = sac.resubmission_meta or {}

        sac.resubmission_meta["resubmission_action"] = form.cleaned_data[
            "resubmission_action"
        ]
        sac.resubmission_meta["resubmission_requester"] = form.cleaned_data[
            "resubmission_requester"
        ]
        sac.resubmission_meta["material_change_reasons"] = form.cleaned_data[
            "material_change_reasons"
        ]
        sac.resubmission_meta["non_material_change_reasons"] = form.cleaned_data[
            "non_material_change_reasons"
        ]

        sac.save(
            event_user=request.user,
            event_type=SubmissionEvent.EventType.RESUBMISSION_META_UPDATED,
        )

        # Second, copy or delete the PDF report as needed.
        resubmission_action = sac.resubmission_meta.get("resubmission_action")
        previous_report_id = sac.resubmission_meta.get("previous_report_id")

        if resubmission_action == RESUBMISSION_ACTION.SFSAC_ONLY:
            audit = Audit.objects.find_audit_or_none(report_id)
            try:
                copy_previous_report_data(
                    previous_report_id=previous_report_id,
                    current_sac=sac,
                    current_audit=audit,
                    user=request.user,
                )
            except Exception as err:
                logger.error(
                    "Unexpected error copying SingleAuditReportFile in resubmission action edit: %s",
                    err,
                )
        elif resubmission_action == RESUBMISSION_ACTION.AUDIT_PDF:
            # 2026-08-11:
            # Should we just hide it, as though it were flagged for deletion?
            # While the record is gone, the s3 object isn't. That's okay?
            SingleAuditReportFile.objects.filter(sac=sac).delete()

        return redirect(
            reverse("audit:SubmissionProgress", kwargs={"report_id": report_id})
        )
