import logging

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View

from config.settings import STATE_ABBREVS
from dissemination.analytics.state import DisseminationStateAnalytics
from dissemination.analytics.trends import DisseminationTrendAnalytics
from dissemination.forms.analytics_forms import AnalyticsFilterForm
from dissemination.templatetags.combine_years import combine_years

logger = logging.getLogger(__name__)


# TODO: Analytics Dashboard
# An example of how we can pull analytics data to the template.
class AnalyticsView(View):
    template = "analytics-state-and-trend.html"

    def get(self, request):
        # URL Params
        state = request.GET.get("state", "")
        year = request.GET.get("year", "")

        if year:
            years = year.split(",")
            years.sort()
            combined_years = combine_years(years)
        else:
            years = []
            combined_years = ""

        # Setup Template Context
        form = AnalyticsFilterForm()
        context = {
            "dashboard_data": {
                "state": state,
                "year": year,
                "years": years,
                "combined_years": combined_years,
            },
            "form": form,
            "state_abbrevs": STATE_ABBREVS,
        }

        # Four Cases:
        # 1. No params are given. Render the blank page.
        # 2. Several years were chose with one state. The trend analytics take precedence, redirect without the state.
        # 3. One year and a state. Make the state analytics queries, and render.
        # 4. Multiple years. Make the trend analytics queries, and render.
        if not state and not year:
            return render(request, self.template, context)

        if len(years) > 1 and state:
            return redirect(f'{reverse("dissemination:Analytics")}?year={year}')

        if len(years) == 1:
            logger.info(f"Gathering state analytics for {state} {year}")
            analytics = DisseminationStateAnalytics(state, year)
            context["dashboard_data"] = context["dashboard_data"] | {
                "state_analytics": {
                    "total": analytics.single_dissemination_count(),
                    "programs_with_repeated_findings": analytics.programs_with_repeated_findings(
                        limit=10
                    ),
                    "top_programs": analytics.top_programs(limit=10),
                    "funding_by_entity_type": analytics.funding_by_entity_type(
                        limit=10
                    ),
                },
            }

        if len(years) > 1:
            logger.info(f"Gathering trend analytics for {state} {years}")
            trend_analytics = DisseminationTrendAnalytics(years)
            context["dashboard_data"] = context["dashboard_data"] | {
                "trend_analytics": {
                    "total_submissions": trend_analytics.total_submissions(),
                    "total_award_volume": trend_analytics.total_award_volume(),
                    "total_findings": trend_analytics.total_findings(),
                    "submissions_with_findings": trend_analytics.submissions_with_findings(),
                    "auditee_risk_profile": trend_analytics.auditee_risk_profile(),
                    "risk_profile_vs_findings": trend_analytics.risk_profile_vs_findings(),
                },
            }

        return render(request, self.template, context)

    def post(self, request):
        form = AnalyticsFilterForm(request.POST)

        if form.is_valid():
            state = form.cleaned_data.get("auditee_state", "")
            years_selected = form.cleaned_data.get("audit_year", [])
            years_string = ",".join(years_selected)

            # Remove the state if several years are selected.
            if len(years_selected) > 1:
                return redirect(
                    f'{reverse("dissemination:Analytics")}?year={years_string}'
                )

            return redirect(
                f'{reverse("dissemination:Analytics")}?state={state}&year={years_string}'
            )
        else:
            # If the form is invalid re-render with the errors
            context = {
                "form": form,
                "state_abbrevs": STATE_ABBREVS,
            }
            return render(request, self.template, context)
