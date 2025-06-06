import logging

from dissemination.analytics.state import DisseminationStateAnalytics
from dissemination.analytics.trends import DisseminationTrendAnalytics
from django.http import JsonResponse
from django.views.generic import View

logger = logging.getLogger(__name__)


# TODO: Analytics Dashboard
# An example of how we can pull analytics data to the template.
class AnalyticsView(View):
    def get(self, request):
        analytics = DisseminationStateAnalytics(
            request.GET.get("year"), request.GET.get("state")
        )
        trend_analytics = DisseminationTrendAnalytics(["2022", "2023", "2024"])

        output_state = {
            # STATE analytics.
            "total": analytics.single_dissemination_count(),
            "programs_with_repeated_findings": analytics.programs_with_repeated_findings(limit=10),
            "top_programs": analytics.top_programs(limit=10),
            "funding_by_entity_type": analytics.funding_by_entity_type(limit=10),
            # TREND analytics.
            "total_submissions": trend_analytics.total_submissions(),
            "total_award_volume": trend_analytics.total_award_volume(),
            "total_findings": trend_analytics.total_findings(),
            "total_submissions_with_findings": trend_analytics.submissions_with_findings(),
            "auditee_risk_profile": trend_analytics.auditee_risk_profile(),
            "risk_profile_vs_findings": trend_analytics.risk_profile_vs_findings(),
        }

        return JsonResponse(data=output_state, safe=False)
