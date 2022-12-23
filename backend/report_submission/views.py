from django.contrib.auth.decorators import login_required
from django.http import QueryDict
from django.shortcuts import render  # noqa: F401
from django.views import generic, View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import json

import api.views
from api.views import EligibilityFormView


# class based views for ...
#class step1(LoginRequiredMixin, TemplateView):
class step1(TemplateView):
    """Basic class for pre-SAC step 1 form."""

    template_name = "report_submission/step-1.html"


class step2(TemplateView):
    """Basic class for pre-SAC step 2 form."""

    template_name = "report_submission/step-2.html"


class step3(TemplateView):
    """Basic class for pre-SAC step 3 form."""

    template_name = "report_submission/step-3.html"


class EligibilityFormView(LoginRequiredMixin, View):
    def post(self, request):
        try:

            data = dict(request.POST.lists())

            response_data = {
                "data": api.views.eligibility_check(request.user, data),
                "user": request.user
            }

            return render(request, "gen-form.html", response_data)
        except:
            print("Error processing data")
