from django.db.models import BigIntegerField, Sum, Q
from django.db.models.functions import Cast
from django.shortcuts import render
from django.views.generic import View

from audit.models import Audit
from audit.models.constants import STATUS, ORGANIZATION_TYPE


class DashboardView(View):
    def get(self, request):
        context = {}

        query = Q(submission_status=STATUS.DISSEMINATED)

        types = [
            ORGANIZATION_TYPE.STATE,
            ORGANIZATION_TYPE.LOCAL,
            ORGANIZATION_TYPE.TRIBAL,
            ORGANIZATION_TYPE.HIGHER_ED,
            ORGANIZATION_TYPE.NON_PROFIT,
        ]

        # Funding by entity type, as a starter
        context['dashboard_data'] = {"labels": [], "values": []}
        for organization_type in types:
            sum = (
                Audit.objects.filter(query)
                .filter(organization_type=organization_type)
                .annotate(
                    total_amount_expended_int=Cast(
                        "audit__federal_awards__total_amount_expended", BigIntegerField()
                    )
                )
                .aggregate(sum=Sum("total_amount_expended_int"))
                ['sum']
            )
            context['dashboard_data']['labels'].append(organization_type)
            context['dashboard_data']['values'].append(sum)

        return render(request, "dashboard.html", context)
