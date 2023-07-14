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
from django.http import JsonResponse

from audit.forms import UploadReportForm

from .fixtures.excel import FORM_SECTIONS

from audit.excel import (
    extract_additional_ueis,
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

from audit.models import Access, ExcelFile, SingleAuditChecklist, SingleAuditReportFile

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
        """
        Get all submissions the user is associated with via Access objects.
        """
        accesses = Access.objects.filter(user=user)
        sac_ids = [access.sac.id for access in accesses]
        data = SingleAuditChecklist.objects.filter(id__in=sac_ids).values(
            "report_id",
            "submission_status",
            auditee_uei=F("general_information__auditee_uei"),
            auditee_name=F("general_information__auditee_name"),
            fiscal_year_end_date=F("general_information__auditee_fiscal_period_end"),
        )
        return data


class EditSubmission(LoginRequiredMixin, generic.View):
    redirect_field_name = "Home"

    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        return redirect(reverse("singleauditchecklist", args=[report_id]))


class ExcelFileHandlerView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    FORM_SECTION_HANDLERS = {
        FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: (
            extract_federal_awards,
            "federal_awards",
        ),
        FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: (
            extract_corrective_action_plan,
            "corrective_action_plan",
        ),
        FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: (
            extract_findings_uniform_guidance,
            "findings_uniform_guidance",
        ),
        FORM_SECTIONS.FINDINGS_TEXT: (extract_findings_text, "findings_text"),
        FORM_SECTIONS.ADDITIONAL_UEIS: (extract_additional_ueis, "additional_ueis"),
    }

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
                **{
                    "file": file,
                    "filename": "temp",
                    "sac_id": sac.id,
                    "form_section": form_section,
                }
            )

            excel_file.full_clean()
            excel_file.save()
            handler, field_name = self.FORM_SECTION_HANDLERS.get(
                form_section, (None, None)
            )
            if handler is None:
                logger.warn(f"no form section found with name {form_section}")
                raise BadRequest()

            audit_data = handler(excel_file.file)
            validate_function = f"validate_{field_name}_json"
            if validate_function in globals() and callable(
                globals()[validate_function]
            ):
                globals()[validate_function](audit_data)

            SingleAuditChecklist.objects.filter(pk=sac.id).update(
                **{field_name: audit_data}
            )

            return redirect("/")
        except SingleAuditChecklist.DoesNotExist:
            logger.warn(f"no SingleAuditChecklist found with report ID {report_id}")
            raise PermissionDenied()
        except ValidationError as e:
            # The good error, where bad rows/columns are sent back in the request.
            # These come back as tuples:
            # [(col1, row1, field1, link1, help-text1), (col2, row2, ...), ...]
            logger.warn(f"{form_section} Excel upload failed validation: {e}")
            return JsonResponse({"errors": list(e), "type": "error_row"}, status=400)
        except MultiValueDictKeyError:
            logger.warn("No file found in request")
            raise BadRequest()
        except KeyError as e:
            logger.warn(f"Field error. Field: {e}")
            return JsonResponse({"errors": str(e), "type": "error_field"}, status=400)


class SingleAuditReportFileHandlerView(
    SingleAuditChecklistAccessRequiredMixin, generic.View
):
    # this is marked as csrf_exempt to enable by-hand testing via tools like Postman. Should be removed when the frontend form is implemented!
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(SingleAuditReportFileHandlerView, self).dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            report_id = kwargs["report_id"]

            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            file = request.FILES["FILES"]

            sar_file = SingleAuditReportFile(
                **{"file": file, "filename": "temp", "sac_id": sac.id}
            )

            sar_file.full_clean()
            sar_file.save()

            return redirect("/")

        except MultiValueDictKeyError:
            logger.warn("No file found in request")
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
                "single_audit_checklist": {
                    "created": True,
                    "created_date": sac.date_created,
                    "created_by": sac.submitted_by,
                    "completed": False,
                    "completed_date": None,
                    "completed_by": None,
                },
                "federal_awards_workbook": {
                    "completed": True if (sac.federal_awards) else False,
                    "completed_date": None,
                    "completed_by": None,
                },
                "audit_information_workbook": {
                    "completed": False,
                    "completed_date": None,
                    "completed_by": None,
                },
                "findings_text_workbook": {
                    "completed": True if (sac.findings_text) else False,
                    "completed_date": None,
                    "completed_by": None,
                },
                "audit_findings_workbook": {
                    "completed": True if (sac.findings_uniform_guidance) else False,
                    "completed_date": None,
                    "completed_by": None,
                },
                "CAP_workbook": {
                    "completed": True if (sac.corrective_action_plan) else False,
                    "completed_date": None,
                    "completed_by": None,
                },
                "additional_UEIs_workbook": {
                    "completed": False,
                    "completed_date": None,
                    "completed_by": None,
                },
                "secondary_auditors_workbook": {
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
                "report_id": report_id,
                "auditee_name": sac.auditee_name,
                "auditee_uei": sac.auditee_uei,
                "user_provided_organization_type": sac.user_provided_organization_type,
            }
            # Add all SF-SAC uploads to determine if the process is complete or not
            context["SF_SAC_completed"] = (
                context["federal_awards_workbook"]["completed"]
                and context["audit_information_workbook"]["completed"]
                and context["findings_text_workbook"]["completed"]
                and context["CAP_workbook"]["completed"]
                and context["additional_UEIs_workbook"]["completed"]
                and context["secondary_auditors_workbook"]["completed"]
            )

            return render(request, "audit/submission-progress.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class PageInput:
    def __init__(self, text="", id="", required=True, hint=None):
        self.text = text
        self.id = id
        self.required = required
        self.hint = hint


class UploadReportView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    def page_number_inputs(self):
        return [
            PageInput(
                "Financial Statement(s) 2 CFR 200.Sl0(a)", "financial_statements"
            ),
            PageInput(
                "Opinion on Financial Statements 2 CFR 200.SlS(a)",
                "financial_statements_opinion",
            ),
            PageInput(
                "Schedule of Expenditures of Federal Awards 2 CFR 200.Sl0(b)",
                "schedule_expenditures",
            ),
            PageInput(
                "Opinion or Disclaimer of Opinion on Schedule of Federal Awards 2 CFR 200.SlS(a)",
                "schedule_expenditures_opinion",
            ),
            PageInput(
                "Uniform Guidance Report on Internal Control 2 CFR 200.SlS(b)",
                "uniform_guidance_control",
            ),
            PageInput(
                "Uniform Guidance Report on Compliance 2 CFR 200.SlS(c)",
                "uniform_guidance_compliance",
            ),
            PageInput("GAS Report on Internal Control 2 CFR 200.SlS(b)", "GAS_control"),
            PageInput(
                "GAS Report on Internal Compliance 2 CFR 200.SlS(b)", "GAS_compliance"
            ),
            PageInput(
                "Schedule of Findings and Questioned Costs 2 CFR 200.SlS(d)",
                "schedule_findings",
            ),
            PageInput(
                "Summary Schedule of Prior Audit Findings 2 CFR 200.Sll(b)",
                "schedule_prior_findings",
                required=False,
                hint="Only required if prior audit findings exist",
            ),
            PageInput(
                "Corrective Action Plan (if findings) 2 CFR 200.Sll(c)",
                "CAP_page",
                required=False,
                hint="Only required if findings exist",
            ),
        ]

    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            context = {
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "auditee_uei": sac.auditee_uei,
                "user_provided_organization_type": sac.user_provided_organization_type,
                "page_number_inputs": self.page_number_inputs(),
            }

            # TODO: check if there's already a PDF in the DB and let the user know

            return render(request, "audit/upload-report.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
        except Exception as e:
            logger.info("Enexpected error in UploadReportView get.\n", e)
            raise BadRequest()

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            form = UploadReportForm(request.POST, request.FILES)

            if form.is_valid():
                file = request.FILES["upload_report"]

                sar_file = SingleAuditReportFile(
                    **{"file": file, "filename": "temp", "sac_id": sac.id}
                )

                sar_file.full_clean()
                sar_file.save()

                # PDF issues can be communicated to the user with form.errors["upload_report"]
                print("Saving form!")
                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))
            else:
                context = {
                    "auditee_name": sac.auditee_name,
                    "report_id": report_id,
                    "auditee_uei": sac.auditee_uei,
                    "user_provided_organization_type": sac.user_provided_organization_type,
                    "page_number_inputs": self.page_number_inputs(),
                    "form": form,
                }
                return render(request, "audit/upload-report.html", context)

        except Exception as e:
            logger.info("Unexpected error in UploadReportView post.\n", e)
            raise BadRequest()
