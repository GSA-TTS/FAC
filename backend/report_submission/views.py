import datetime
import json
from django.shortcuts import render, redirect  # noqa: F401
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

import api.views


def parse_body_data(request_body):
    body_unicode = request_body.decode("utf-8")
    body_data = json.loads(body_unicode)
    return body_data


class ReportSubmissionRedirectView(View):
    def get(self, request):
        return redirect(reverse("eligibility"))


# Step 1
class EligibilityFormView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "report_submission/step-1.html")

    # render eligibility form

    # gather/save step 1 info, redirect to step 2
    def post(self, post_request):
        eligibility = api.views.eligibility_check(post_request.user, post_request.POST)
        if eligibility.get("eligible"):
            return redirect(reverse("auditeeinfo"))

        print("Eligibility data error: ", eligibility)
        return redirect(reverse("eligibility"))


# Step 2
class AuditeeInfoFormView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "report_submission/step-2.html")

    # render auditee info form

    # gather/save step 2 info, redirect to step 3
    def post(self, post_request):
        # TODO: Wrap in better error-checking
        start = datetime.datetime.strptime(
            post_request.POST.get("auditee_fiscal_period_start", "01/01/1970"),
            "%m/%d/%Y",
        )
        end = datetime.datetime.strptime(
            post_request.POST.get("auditee_fiscal_period_end", "01/01/1970"),
            "%m/%d/%Y",
        )

        formatted_post = {
            "csrfmiddlewaretoken": post_request.POST.get("csrfmiddlewaretoken"),
            "auditee_uei": post_request.POST.get("auditee_uei"),
            "auditee_fiscal_period_start": start.strftime("%Y-%m-%d"),
            "auditee_fiscal_period_end": end.strftime("%Y-%m-%d"),
        }

        info_check = api.views.auditee_info_check(post_request.user, formatted_post)
        if info_check.get("errors"):
            return redirect(reverse("auditeeinfo"))
            print("Auditee info data error: ", info_check)

        return redirect(reverse("accessandsubmission"))


# Step 3
class AccessAndSubmissionFormView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "report_submission/step-3.html")

    # render access-submission form

    # gather/save step 3 info, redirect to step ...4?
    def post(self, post_request):
        formatted_post = {
            "certifying_auditee_contact": post_request.POST.get(
                "auditee_certifying_official_email", ""
            ),
            "certifying_auditor_contact": post_request.POST.get(
                "auditor_certifying_official_email", ""
            ),
            "auditee_contacts": post_request.POST.getlist("auditee_contacts_email", []),
            "auditor_contacts": post_request.POST.getlist("auditor_contacts_email", []),
        }

        result = api.views.access_and_submission_check(
            post_request.user, formatted_post
        )
        report_id = result.get("report_id")

        if report_id:
            # This should redirect to the commented-out line, but we'll just
            # redirect to the JSON representation of the data until the correct
            # page is up:
            # return redirect(f"/audit/{report_id}")
            return redirect(f"/sac/edit/{report_id}")
        print("Error processing data: ", result)
        return redirect(reverse("accessandsubmission"))
