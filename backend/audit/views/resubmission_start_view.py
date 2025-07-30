from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View

from audit.formlib import ResubmissionStartForm
from config.settings import ENVIRONMENT


class ResubmissionStartView(LoginRequiredMixin, View):
    """
    A form submission for beginning a resubmission.
    """

    template_name = "audit/resubmission_start_form.html"

    def get(self, request, *args, **kwargs):
        # Only run in non-production environments for now.
        if ENVIRONMENT == "PRODUCTION":
            return redirect(reverse("config:Home"))

        return render(request, self.template_name)

    def post(self, request):
        # Only run in non-production environments for now.
        if ENVIRONMENT == "PRODUCTION":
            return redirect(reverse("config:Home"))

        form = ResubmissionStartForm(request.POST)

        # If the form is not valid, reload to display the errors
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {"form": form, "form_user_input": form.cleaned_data},
            )

        # The form is valid. Populate resubmission_meta and store it to the user profile.
        # Then, send them to step 1.
        report_id = form.cleaned_data["report_id"]
        previous_row_id = form.cleaned_data["sac_row_id"]

        # Save the resub metadata to the user profile. Overwrites other user profile data.
        resubmission_meta = {
            "is_resubmission": True,
            "resubmission_meta": {
                "previous_report_id": report_id,
                "previous_row_id": previous_row_id,
            },
        }
        user = request.user
        user.profile.entry_form_data = resubmission_meta
        user.profile.save()

        # Send to step 1 of presubmission eligibility.
        # resubmission_meta will be used again on audit creation after step 3.
        return redirect(reverse("report_submission:auditeeinfo"))
