from django.views import generic
from django.shortcuts import render, redirect
from django.db.models import F
from django.urls import reverse

from audit.models import SingleAuditChecklist


class MySubmissions(generic.View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            url = reverse('Home')
            return redirect(url)
        template_name = "audit/my_submissions.html"
        next_page = 'MySubmissions'  # TO DO Replace with ReportSubmissions alias
        data = MySubmissions.fetch_my_subnissions(request.user)
        extra_context = {'data': data, 'next_page': next_page}
        return render(request, template_name, extra_context)

    @ classmethod
    def fetch_my_subnissions(cls, user):
        data = SingleAuditChecklist.objects.all().values(
            "report_id",
            "submission_status",
            auditee_uei=F('general_information__auditee_uei'),
            auditee_name=F('general_information__auditee_name'),
            fiscal_year_end_date=F('general_information__auditee_fiscal_period_end')
        ).filter(submitted_by=user)
        return data
