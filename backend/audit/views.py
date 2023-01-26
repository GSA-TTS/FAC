from django.views import generic
from django.shortcuts import render
from django.db.models import F
from django.contrib.auth.mixins import LoginRequiredMixin


from .models import SingleAuditChecklist
from .forms import SubmissionForm


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

        template_name = "audit/edit_submission.html"
        report_id = kwargs["report_id"]
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        form = SubmissionForm(instance=sac)
        next_link = "Home"
        context = {"report_id": report_id, "form": form, "next_link": next_link}
        return render(request, template_name, context)
