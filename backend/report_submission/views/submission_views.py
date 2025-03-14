import logging

from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

import api.views


from audit.utils import Util
from config.settings import DOLLAR_THRESHOLDS

from report_submission.forms import AuditeeInfoForm

logger = logging.getLogger(__name__)


class ReportSubmissionRedirectView(View):
    def get(self, request):
        return redirect(reverse("report_submission:eligibility"))


# Step 1
class EligibilityFormView(LoginRequiredMixin, View):
    def get(self, request):
        args = {
            "step": 1,
            "dollar_thresholds": [
                dict_item["message"] for dict_item in DOLLAR_THRESHOLDS
            ],
        }

        return render(request, "report_submission/step-1.html", args)

    # gather/save step 1 info, redirect to step 2
    def post(self, post_request):
        eligibility = api.views.eligibility_check(post_request.user, post_request.POST)
        if eligibility.get("eligible"):
            return redirect(reverse("report_submission:auditeeinfo"))

        return redirect(reverse("report_submission:eligibility"))


# Step 2
class AuditeeInfoFormView(LoginRequiredMixin, View):
    def get(self, request):
        entry_form_data = request.user.profile.entry_form_data
        eligible = api.views.eligibility_check(request.user, entry_form_data)

        # Prevent users from skipping the eligibility form
        if not eligible.get("eligible"):
            return redirect(reverse("report_submission:eligibility"))
        else:
            args = {}
            args["step"] = 2
            args["form"] = AuditeeInfoForm()
            return render(request, "report_submission/step-2.html", args)

    # render auditee info form

    # gather/save step 2 info, redirect to step 3
    def post(self, request):
        form = AuditeeInfoForm(request.POST)
        if not form.is_valid():
            context = {
                "form": form,
                "step": 2,
            }
            return render(request, "report_submission/step-2.html", context)

        formatted_post = {
            "csrfmiddlewaretoken": request.POST.get("csrfmiddlewaretoken"),
            "auditee_uei": form.cleaned_data["auditee_uei"].upper(),
            "auditee_address_line_1": request.POST.get("auditee_address_line_1"),
            "auditee_city": request.POST.get("auditee_city"),
            "auditee_state": request.POST.get("auditee_state"),
            "auditee_zip": request.POST.get("auditee_zip"),
            "auditee_fiscal_period_start": form.cleaned_data[
                "auditee_fiscal_period_start"
            ].strftime("%Y-%m-%d"),
            "auditee_fiscal_period_end": form.cleaned_data[
                "auditee_fiscal_period_end"
            ].strftime("%Y-%m-%d"),
        }

        info_check = api.views.auditee_info_check(request.user, formatted_post)
        if info_check.get("errors"):
            return redirect(reverse("report_submission:auditeeinfo"))

        return redirect(reverse("report_submission:accessandsubmission"))


# Step 3
class AccessAndSubmissionFormView(LoginRequiredMixin, View):
    def get(self, request):
        info_check = api.views.auditee_info_check(
            request.user, request.user.profile.entry_form_data
        )

        # Prevent users from skipping the auditee info form
        if info_check.get("errors"):
            return redirect(reverse("report_submission:auditeeinfo"))
        else:
            args = {}
            args["step"] = 3
            return render(request, "report_submission/step-3.html", args)

    def post(self, request):

        with transaction.atomic():

            result = api.views.access_and_submission_check(request.user, request.POST)

            report_id = result.get("report_id")

            if report_id:
                return Util.validate_redirect_url(
                    f"/report_submission/general-information/{report_id}"
                )
            else:
                return render(
                    request, "report_submission/step-3.html", context=result, status=400
                )
