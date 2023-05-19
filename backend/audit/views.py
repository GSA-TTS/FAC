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

from .fixtures.excel import (
    FEDERAL_AWARDS_EXPENDED,
    CORRECTIVE_ACTION_PLAN,
    FINDINGS_TEXT,
    FINDINGS_UNIFORM_GUIDANCE,
)

from audit.excel import (
    extract_federal_awards,
    extract_corrective_action_plan,
    extract_findings_text,
    extract_findings_uniform_guidance,
)
from audit.mixins import (
    CertifyingAuditeeRequiredMixin,
    CertifyingAuditorRequiredMixin,
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import ExcelFile, SingleAuditChecklist
from audit.validators import (
    validate_federal_award_json,
    validate_corrective_action_plan_json,
    validate_findings_text_json,
    validate_findings_uniform_guidance_json,
)

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


class ExcelFileHandlerView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    # this is marked as csrf_exempt to enable by-hand testing via tools like Postman. Should be removed when the frontend form is implemented!
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ExcelFileHandlerView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            report_id = kwargs["report_id"]

            form_section = kwargs["form_section"]

            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            file = request.FILES["FILES"]

            excel_file = ExcelFile(
                **{"file": file, "filename": "temp", "sac_id": sac.id}
            )

            excel_file.full_clean()
            excel_file.save()

            if form_section == FEDERAL_AWARDS_EXPENDED:
                audit_data = extract_federal_awards(excel_file.file)
                validate_federal_award_json(audit_data)
                SingleAuditChecklist.objects.filter(pk=sac.id).update(
                    federal_awards=audit_data
                )
            elif form_section == CORRECTIVE_ACTION_PLAN:
                audit_data = extract_corrective_action_plan(excel_file.file)
                validate_corrective_action_plan_json(audit_data)
                SingleAuditChecklist.objects.filter(pk=sac.id).update(
                    corrective_action_plan=audit_data
                )
            elif form_section == FINDINGS_UNIFORM_GUIDANCE:
                audit_data = extract_findings_uniform_guidance(excel_file.file)
                validate_findings_uniform_guidance_json(audit_data)
                SingleAuditChecklist.objects.filter(pk=sac.id).update(
                    findings_uniform_guidance=audit_data
                )
            elif form_section == FINDINGS_TEXT:
                audit_data = extract_findings_text(excel_file.file)
                validate_findings_text_json(audit_data)
                SingleAuditChecklist.objects.filter(pk=sac.id).update(
                    findings_text=audit_data
                )
            else:
                logger.warn(f"no form section found with name {form_section}")
                raise BadRequest()

            return redirect("/")
        except SingleAuditChecklist.DoesNotExist:
            logger.warn(f"no SingleAuditChecklist found with report ID {report_id}")
            raise PermissionDenied()
        except ValidationError as e:
            logger.warn(f"{form_section} Excel upload failed validation: {e}")
            raise BadRequest(e)
        except MultiValueDictKeyError:
            logger.warn("no file found in request")
            raise BadRequest()


class ReadyForCertificationView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }
            return render(request, "audit/ready-for-certification.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            sac.transition_to_ready_for_certification()
            sac.save()

            return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class AuditorCertificationView(CertifyingAuditorRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }

            return render(request, "audit/auditor-certification.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            sac.transition_to_auditor_certified()
            sac.save()

            return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class AuditeeCertificationView(CertifyingAuditeeRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }

            return render(request, "audit/auditee-certification.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            sac.transition_to_auditee_certified()
            sac.save()

            return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class CertificationView(CertifyingAuditeeRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }

            return render(request, "audit/certification.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            sac.transition_to_certified()
            sac.save()

            return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class SubmissionView(CertifyingAuditeeRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }

            return render(request, "audit/submission.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            sac.transition_to_submitted()
            sac.save()

            return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class SubmissionProgressView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "single_audit_checklist": {
                    "created": True,
                    "created_date": sac.date_created,
                    "created_by": sac.submitted_by,
                    "completed": False,
                    "completed_date": None,
                    "completed_by": None,
                },
                "audit_report": {
                    "completed": False,
                    "completed_date": None,
                    "completed_by": None,
                },
                "certification": {
                    "auditee_certified": sac.is_auditee_certified,
                    "auditor_certified": sac.is_auditor_certified,
                },
                "submission": {
                    "completed": sac.is_submitted,
                    "completed_date": None,
                    "completed_by": None,
                },
            }

            return render(request, "audit/submission-progress.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
