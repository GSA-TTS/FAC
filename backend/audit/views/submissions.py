import logging

from django.views import generic
from django.shortcuts import render, redirect
from django.db.models import F, Q
from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse

from audit.mixins import (
    CertifyingAuditeeRequiredMixin,
)
from audit.models import (
    Audit,
    Access,
)
from audit.models.constants import STATUS
from audit.models.utils import get_friendly_submission_status
from audit.models.viewflow import audit_transition
from audit.decorators import verify_status
from dissemination.remove_workbook_artifacts import audit_remove_workbook_artifacts

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)


class MySubmissions(LoginRequiredMixin, generic.View):
    redirect_field_name = "Home"

    def get(self, request, *args, **kwargs):
        template_name = "audit/audit_submissions/audit_submissions.html"
        new_link = "report_submission"
        edit_link = "audit:EditSubmission"
        submissions = MySubmissions.fetch_my_submissions(request.user)

        data = {"completed_audits": [], "in_progress_audits": []}
        for audit in submissions:
            audit["submission_status"] = get_friendly_submission_status(
                audit["submission_status"]
            )
            if audit["submission_status"] in ["Submitted", "Disseminated"]:
                data["completed_audits"].append(audit)
            else:
                data["in_progress_audits"].append(audit)

        context = {
            "data": data,
            "new_link": new_link,
            "edit_link": edit_link,
        }
        return render(request, template_name, context)

    @classmethod
    def fetch_my_submissions(cls, user):
        """
        Get all submissions the user is associated with via Access objects.
        """
        accesses = Access.objects.filter(user=user)
        audit_ids = [access.audit.id for access in accesses]
        data = Audit.objects.filter(
            Q(id__in=audit_ids) & ~Q(submission_status=STATUS.FLAGGED_FOR_REMOVAL)
        ).values(
            "report_id",
            "submission_status",
            "auditee_uei",
            "auditee_name",
            fiscal_year_end_date=F(
                "audit__general_information__auditee_fiscal_period_end"
            ),
        )
        return data


class EditSubmission(LoginRequiredMixin, generic.View):
    redirect_field_name = "Home"

    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        return redirect(reverse("audit", args=[report_id]))


class SubmissionView(CertifyingAuditeeRequiredMixin, generic.View):
    @verify_status(STATUS.AUDITEE_CERTIFIED)
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        try:
            audit = Audit.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": audit.submission_status,
            }

            return render(request, "audit/submission.html", context)
        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    @verify_status(STATUS.AUDITEE_CERTIFIED)
    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        try:
            # remove try/except once we are ready to deprecate SAC.
            audit = Audit.objects.get(report_id=report_id)
            audit_errors = audit.validate()
            if audit_errors:
                context = {"report_id": report_id, "errors": audit_errors}

                return render(
                    request,
                    "audit/cross-validation/cross-validation-results.html",
                    context,
                )

            audit_transition(request=request, audit=audit, event=STATUS.DISSEMINATED)
            audit_remove_workbook_artifacts(audit)

            return redirect(reverse("audit:MySubmissions"))

        except Audit.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
