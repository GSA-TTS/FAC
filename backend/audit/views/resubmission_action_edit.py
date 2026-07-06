from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View

from audit.formlib import ResubmissionActionForm
from audit.mixins import SingleAuditChecklistAccessRequiredMixin
from audit.models import SingleAuditChecklist


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

        sac.save()

        return redirect(
            reverse("audit:SubmissionProgress", kwargs={"report_id": report_id})
        )
