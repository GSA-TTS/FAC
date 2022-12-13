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
class step1(LoginRequiredMixin, TemplateView):
    """Basic class for home."""

    template_name = "gen-form.html"


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
