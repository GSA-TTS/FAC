import logging

from dissemination.analytics.state import DisseminationStateAnalytics
from django.shortcuts import render
from django.views.generic import View

logger = logging.getLogger(__name__)

# TODO: Analytics Dashboard
# An example of how we can pull analytics data to the template.
class AnalyticsView(View):
    def get(self, request):
        analytics = DisseminationStateAnalytics(request.GET['year'], request.GET['state'])

        return render(request, "my_html_page.html", {
            "total": analytics.single_dissemination_count(),
            "programs_with_repeated_findings": analytics.programs_with_repeated_findings(),
            "top_programs": analytics.top_programs(),
            "funding_by_entity_type": analytics.funding_by_entity_type(),
        })
