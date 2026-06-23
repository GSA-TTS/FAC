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

        resubmission_action = (
            sac.resubmission_meta.get("resubmission_action")
            if sac.resubmission_meta
            else None
        )

        form = ResubmissionActionForm(
        initial={
            "resubmission_action": resubmission_action,
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

        resubmission_action = form.cleaned_data["resubmission_action"]

        sac.resubmission_meta = sac.resubmission_meta or {}
        sac.resubmission_meta["resubmission_action"] = resubmission_action
        sac.save()

        return redirect(
            reverse("audit:SubmissionProgress", kwargs={"report_id": report_id})
        )
