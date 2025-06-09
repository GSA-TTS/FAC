import logging

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View

from config.settings import STATE_ABBREVS
from dissemination.analytics.state import DisseminationStateAnalytics
from dissemination.analytics.trends import DisseminationTrendAnalytics
from dissemination.forms.dashboard_forms import AnalyticsFilterForm

logger = logging.getLogger(__name__)


# TODO: Analytics Dashboard
# An example of how we can pull analytics data to the template.
class AnalyticsView(View):
    def get(self, request):
        # URL Params
        state = request.GET.get("state")
        year = request.GET.get("year")

        # Setup Template Context
        form = AnalyticsFilterForm()
        context = {
            "dashboard_data": {"state": state, "year": year},
            "form": form,
            "state_abbrevs": STATE_ABBREVS,
        }

        # Make Queries, Add Results to Context
        analytics = DisseminationStateAnalytics(state, year)
        trend_analytics = DisseminationTrendAnalytics(["2022", "2023", "2024"])
        context["dashboard_data"] = context["dashboard_data"] | {
            "state_analytics": {
                "total": analytics.single_dissemination_count(),
                "programs_with_repeated_findings": analytics.programs_with_repeated_findings(
                    limit=10
                ),
                "top_programs": analytics.top_programs(limit=10),
                "funding_by_entity_type": analytics.funding_by_entity_type(limit=10),
            },
            "trend_analytics": {
                "total_submissions": trend_analytics.total_submissions(),
                "total_award_volume": trend_analytics.total_award_volume(),
                "total_findings": trend_analytics.total_findings(),
                "total_submissions_with_findings": trend_analytics.submissions_with_findings(),
                "auditee_risk_profile": trend_analytics.auditee_risk_profile(),
                "risk_profile_vs_findings": trend_analytics.risk_profile_vs_findings(),
            },
        }

        return render(request, "dashboard.html", context)

    def post(self, request):
        form = AnalyticsFilterForm(request.POST)
        
        if form.is_valid():
            print("maaan", form.cleaned_data)
            state = form.cleaned_data.get("auditee_state")
            years = ",".join(form.cleaned_data.get("audit_year"))
            
            return redirect(f"{reverse("dissemination:Analytics")}?state={state}&year={years}")
        else:
            # It should never be, but if the form is invalid re-render with the errors
            context = {
                "form": form,
            }
            return render(request, "dashboard.html", context)
