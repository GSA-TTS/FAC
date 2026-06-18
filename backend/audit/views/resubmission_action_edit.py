from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.generic import View

from audit.formlib import ResubmissionActionForm
from audit.mixins import SingleAuditChecklistAccessRequiredMixin


class ResubmissionActionEditView(SingleAuditChecklistAccessRequiredMixin, View):
    template_name = "audit/resubmission_action_edit.html"

    def get(self, request, *args, **kwargs):
        entry_form_data = request.user.profile.entry_form_data or {}

        form = ResubmissionActionForm(
            initial={
                "resubmission_action": entry_form_data.get("resubmission_action"),
            }
        )

        return render(
            request,
            self.template_name,
            {
                "form": form,
                "report_id": kwargs["report_id"],
            },
        )

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        entry_form_data = request.user.profile.entry_form_data or {}

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

        entry_form_data["resubmission_action"] = form.cleaned_data[
            "resubmission_action"
        ]

        request.user.profile.entry_form_data = entry_form_data
        request.user.profile.save()

        return redirect(
            reverse("audit:SubmissionProgress", kwargs={"report_id": report_id})
        )
