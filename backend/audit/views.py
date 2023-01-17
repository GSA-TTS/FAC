from django.views import generic
from django.shortcuts import render
from django.db.models import F
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import SingleAuditChecklist

UEI_TOOLTIP = """
Unique Entity Identifuer (UEI)
The Unique Entity Identifier (UEI) for an awardee
or recipent is an alphanumeric code created in
the System for Award Management (SAM.gov)
that is used to uniquely identify specific
commenrcial, nonprofit or business entities
registered to do business with the federal
givernment
"""


class MySubmissions(LoginRequiredMixin, generic.View):
    redirect_field_name = "Home"

    def get(self, request, *args, **kwargs):

        template_name = "audit/my_submissions.html"
        next_page = "audit:MySubmissions"  # TO DO Replace with ReportSubmissions alias
        data = MySubmissions.fetch_my_subnissions(request.user)
        extra_context = {"data": data, "uei_tip": UEI_TOOLTIP, "next_page": next_page}
        return render(request, template_name, extra_context)

    @classmethod
    def fetch_my_subnissions(cls, user):
        data = (
            SingleAuditChecklist.objects.all()
            .values(
                "report_id",
                "submission_status",
                auditee_uei=F("general_information__auditee_uei"),
                auditee_name=F("general_information__auditee_name"),
                fiscal_year_end_date=F(
                    "general_information__auditee_fiscal_period_end"
                ),
            )
            .filter(submitted_by=user)
        )
        return data
