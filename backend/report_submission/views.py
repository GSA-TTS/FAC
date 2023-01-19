from django.contrib.auth.decorators import login_required
from django.http import QueryDict, request
from django.shortcuts import render, redirect  # noqa: F401
from django.urls import reverse
from django.views import generic, View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import json

import api.views
from api.views import EligibilityFormView


def parse_body_data(request_data):
    body_unicode = request_data.body.decode('utf-8')
    body_data = json.loads(body_unicode)
    return body_data


# class based views for ...
# class Step(View):
#     def get(self, request):
#         step = request.GET.get('step', 1)
#         step = 1 if step not in (1, 2, 3) else step
#         extra_context = {'step': step}
#         template_name = f'report_submission/step-{step}.html'
#         return render(request, template_name, extra_context)
#
#     def post(self, request):
#         pass

# class step1(LoginRequiredMixin, TemplateView):

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
        body_data = parse_body_data(request_data=post_request)

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
        body_data = parse_body_data(request_data=post_request)

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
        body_data = parse_body_data(request_data=post_request)

        try:
            api.views.eligibility_check(post_request.user, body_data)

            return redirect(reverse("auditeeinfo"))
        except Exception as ex:
            print("Error processing data: ", ex)
            return redirect(reverse("eligibility"))
