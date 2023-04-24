import logging

from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.db.models import F
from django.core.exceptions import BadRequest, PermissionDenied, ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator

from audit.excel import extract_federal_awards
from audit.models import Access, ExcelFile, SingleAuditChecklist
from audit.validators import validate_federal_award_json

logger = logging.getLogger(__name__)


class MySubmissions(LoginRequiredMixin, generic.View):
    redirect_field_name = "Home"

    def get(self, request, *args, **kwargs):
        template_name = "audit/my_submissions.html"
        new_link = "report_submission"
        edit_link = "audit:EditSubmission"

        data = MySubmissions.fetch_my_submissions(request.user)
        context = {
            "data": data,
            "new_link": new_link,
            "edit_link": edit_link,
        }
        return render(request, template_name, context)

    @classmethod
    def fetch_my_submissions(cls, user):
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
        report_id = kwargs["report_id"]
        return redirect(reverse("singleauditchecklist", args=[report_id]))


class FederalAwardsExcelFileView(LoginRequiredMixin, generic.View):
    # this is marked as csrf_exempt to enable by-hand testing via tools like Postman. Should be removed when the frontend form is implemented!
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(FederalAwardsExcelFileView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            report_id = kwargs["report_id"]

            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            file = request.FILES["FILES"]

            excel_file = ExcelFile(
                **{"file": file, "filename": "temp", "sac_id": sac.id}
            )

            excel_file.full_clean()
            excel_file.save()

            federal_awards = extract_federal_awards(excel_file.file)
            validate_federal_award_json(federal_awards)

            SingleAuditChecklist.objects.filter(pk=sac.id).update(
                federal_awards=federal_awards
            )

            return redirect("/")
        except SingleAuditChecklist.DoesNotExist:
            logger.warn(f"no SingleAuditChecklist found with report ID {report_id}")
            raise PermissionDenied()
        except ValidationError as e:
            logger.warn(f"Federal Awards Excel upload failed validation: {e}")
            raise BadRequest()
        except MultiValueDictKeyError:
            logger.warn("no file found in request")
            raise BadRequest()


class ReadyForCertificationView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            # this should probably be a permission mixin
            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            return render(request, "audit/ready-for-certification.html")
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            # this should probably be a permission mixin
            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            sac.transition_to_ready_for_certification()
            sac.save()

            return redirect(reverse("audit:AuditorCertification", args=[report_id]))

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class AuditorCertificationView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            # this should probably be a permission mixin
            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            return render(request, "audit/auditor-certification.html")
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            # this should probably be a permission mixin
            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            sac.transition_to_auditor_certified()
            sac.save()

            return redirect(reverse("audit:AuditeeCertification", args=[report_id]))

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class AuditeeCertificationView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            # this should probably be a permission mixin
            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            return render(request, "audit/auditee-certification.html")
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            # this should probably be a permission mixin
            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            sac.transition_to_auditee_certified()
            sac.save()

            return redirect(reverse("audit:Certification", args=[report_id]))

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class CertificationView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            # this should probably be a permission mixin
            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            return render(request, "audit/certification.html")
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            # this should probably be a permission mixin
            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            sac.transition_to_certified()
            sac.save()

            return redirect(reverse("audit:Submission", args=[report_id]))

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class SubmissionView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            # this should probably be a permission mixin
            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            return render(request, "audit/submission.html")
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            # this should probably be a permission mixin
            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            sac.transition_to_submitted()
            sac.save()

            return render(request, "audit/submission.html")

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
