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

        # The form is valid. Populate previous_report_data and resubmission_meta, and store it to the user profile.
        previous_report_data = form.cleaned_data["previous_report_data"]
        resubmission_meta = form.cleaned_data["resubmission_meta"]

        # Save the previous report data and resubmission metadata to the user profile. Overwrites other user profile data.
        profile_data = previous_report_data | {
            "is_resubmission": True,
            "resubmission_meta": resubmission_meta,
        }
        user = request.user
        user.profile.entry_form_data = profile_data
        user.profile.save()

        # Send to step 2 of presubmission eligibility.
        # Step 1 (UEI and fiscal period) must remain unchanged.
        return redirect(reverse("report_submission:eligibility"))
