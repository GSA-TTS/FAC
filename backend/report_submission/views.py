from django.shortcuts import render, redirect  # noqa: F401
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
import json

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
        body_data = parse_body_data(request_data=post_request.body)

        debuggable = post_request.body
        print ("\n", debuggable, "\n")

        try:
            api.views.eligibility_check(post_request.user, body_data)

            return redirect(reverse("auditeeinfo"))
        except Exception as ex:
            print("Error processing data: ", ex)
            return redirect(reverse("eligibility"))


# Step 2
class AuditeeInfoFormView(LoginRequiredMixin, View):
    def get(self, request):
        print(request.body)
        return render(request, "report_submission/step-2.html")

    # render auditee info form

    # gather/save step 2 info, redirect to step 3
    def post(self, post_request):
        body_data = parse_body_data(request_data=post_request.body)

        try:
            api.views.auditee_info_check(post_request.user, body_data)

            return redirect(reverse("accessandsubmission"))
        except Exception as ex:
            print("Error processing data: ", ex)
            return redirect(reverse("auditeeinfo"))
        return redirect(reverse("accessandsubmissioninfo"))


# Step 3
class AccessAndSubmissionFormView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "report_submission/step-3.html")

    # render access-submission form

    # gather/save step 3 info, redirect to step ...4?
    def post(self, post_request):
        body_data = parse_body_data(request_data=post_request.body)

        result = api.views.access_and_submission_check(post_request.user, body_data)
        report_id = result.get("report_id")

        if report_id:
            # This should redirect to the following line without the
            # hash, but we're doing this until we stand up the next form
            # page:
            return redirect(f"/audit/#{report_id}")
        else:
            print("Error processing data: ", result)
            return redirect(reverse("accessandsubmissioninfo"))
