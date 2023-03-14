from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.db.models import F
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.decorators import method_decorator

from audit.excel import extract_federal_awards
from audit.models import ExcelFile, SingleAuditChecklist
from audit.validators import validate_federal_award_json


class MySubmissions(LoginRequiredMixin, generic.View):
    redirect_field_name = "Home"

    def get(self, request, *args, **kwargs):

        template_name = "audit/my_submissions.html"
        new_link = "report_submission"
        edit_link = "audit:EditSubmission"

        data = MySubmissions.fetch_my_subnissions(request.user)
        context = {
            "data": data,
            "new_link": new_link,
            "edit_link": edit_link,
        }
        return render(request, template_name, context)

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


class EditSubmission(LoginRequiredMixin, generic.View):
    redirect_field_name = "Home"

    def get(self, request, *args, **kwargs):

        # template_name = "audit/edit_submission.html"
        report_id = kwargs["report_id"]
        # sac = SingleAuditChecklist.objects.get(report_id=report_id)
        # return render(request, template_name, context)
        return redirect(reverse("singleauditchecklist", args=[report_id]))


class FederalAwardsExcelFileView(generic.View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(FederalAwardsExcelFileView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        sac = SingleAuditChecklist.objects.get(report_id=report_id)

        excel_file = ExcelFile(
            **{"file": request.FILES["FILES"], "filename": "temp", "sac_id": sac.id}
        )

        excel_file.full_clean()

        federal_awards = extract_federal_awards(excel_file.file)

        validate_federal_award_json(federal_awards)

        excel_file.save()

        return redirect("/")
