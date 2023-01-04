from django.contrib.auth.decorators import login_required
from django.http import QueryDict, request
from django.shortcuts import render  # noqa: F401
from django.views import generic, View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
import json

import api.views
from api.views import EligibilityFormView


# class based views for ...
class Step(LoginRequiredMixin, View):
    def get(self, request: request):
        step = request.GET.get('step', 1)
        step = 1 if step not in (1, 2, 3) else step
        extra_context = {'step': step}
        template_name = f'report_submission/step-{step}.html'
        return render(request, template_name, extra_context)


# class step1(LoginRequiredMixin, TemplateView):


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
