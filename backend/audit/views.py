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

from config.settings import (
    AGENCY_NAMES,
    GAAP_RESULTS,
    SP_FRAMEWORK_BASIS,
    SP_FRAMEWORK_OPINIONS,
)
from .fixtures.excel import FORM_SECTIONS, UNKNOWN_WORKBOOK

from audit.cross_validation import sac_validation_shape, submission_progress_check
from audit.excel import (
    extract_additional_ueis,
    extract_additional_eins,
    extract_federal_awards,
    extract_corrective_action_plan,
    extract_findings_text,
    extract_findings_uniform_guidance,
    extract_secondary_auditors,
    extract_notes_to_sefa,
)
from audit.forms import (
    AuditInfoForm,
    AuditorCertificationStep1Form,
    AuditorCertificationStep2Form,
    AuditeeCertificationStep1Form,
    AuditeeCertificationStep2Form,
)
from audit.mixins import (
    CertifyingAuditeeRequiredMixin,
    CertifyingAuditorRequiredMixin,
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    Access,
    ExcelFile,
    LateChangeError,
    SingleAuditChecklist,
    SingleAuditReportFile,
)
from audit.utils import ExcelExtractionError
from audit.validators import (
    validate_additional_ueis_json,
    validate_additional_eins_json,
    validate_audit_information_json,
    validate_auditee_certification_json,
    validate_auditor_certification_json,
    validate_corrective_action_plan_json,
    validate_federal_award_json,
    validate_findings_text_json,
    validate_findings_uniform_guidance_json,
    validate_notes_to_sefa_json,
    validate_secondary_auditors_json,
)
from audit.viewlib import UploadReportView  # noqa


logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)


class MySubmissions(LoginRequiredMixin, generic.View):
    redirect_field_name = "Home"

    def get(self, request, *args, **kwargs):
        template_name = "audit/my_submissions.html"
        new_link = "report_submission"
        edit_link = "audit:EditSubmission"

        submissions = MySubmissions.fetch_my_submissions(request.user)

        data = {"completed_audits": [], "in_progress_audits": []}
        for audit in submissions:
            audit["submission_status"] = (
                audit["submission_status"].replace("_", " ").title()
            )  # auditee_certified --> Auditee Certified
            if audit["submission_status"] == "Submitted":
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
        FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: {
            "extractor": extract_federal_awards,
            "field_name": "federal_awards",
            "validator": validate_federal_award_json,
        },
        FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: {
            "extractor": extract_corrective_action_plan,
            "field_name": "corrective_action_plan",
            "validator": validate_corrective_action_plan_json,
        },
        FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: {
            "extractor": extract_findings_uniform_guidance,
            "field_name": "findings_uniform_guidance",
            "validator": validate_findings_uniform_guidance_json,
        },
        FORM_SECTIONS.FINDINGS_TEXT: {
            "extractor": extract_findings_text,
            "field_name": "findings_text",
            "validator": validate_findings_text_json,
        },
        FORM_SECTIONS.ADDITIONAL_UEIS: {
            "extractor": extract_additional_ueis,
            "field_name": "additional_ueis",
            "validator": validate_additional_ueis_json,
        },
        FORM_SECTIONS.ADDITIONAL_EINS: {
            "extractor": extract_additional_eins,
            "field_name": "additional_eins",
            "validator": validate_additional_eins_json,
        },
        FORM_SECTIONS.SECONDARY_AUDITORS: {
            "extractor": extract_secondary_auditors,
            "field_name": "secondary_auditors",
            "validator": validate_secondary_auditors_json,
        },
        FORM_SECTIONS.NOTES_TO_SEFA: {
            "extractor": extract_notes_to_sefa,
            "field_name": "notes_to_sefa",
            "validator": validate_notes_to_sefa_json,
        },
    }

    def _create_excel_file(self, file, sac_id, form_section):
        excel_file = ExcelFile(
            **{
                "file": file,
                "filename": "temp",
                "sac_id": sac_id,
                "form_section": form_section,
            }
        )
        excel_file.full_clean()
        return excel_file

    def _extract_and_validate_data(self, form_section, excel_file):
        handler_info = self.FORM_SECTION_HANDLERS.get(form_section)
        if handler_info is None:
            logger.warning("No form section found with name %s", form_section)
            raise BadRequest()
        audit_data = handler_info["extractor"](excel_file.file)
        validator = handler_info.get("validator")
        if validator is not None and callable(validator):
            validator(audit_data)
        return audit_data

    def _save_audit_data(self, sac, form_section, audit_data):
        handler_info = self.FORM_SECTION_HANDLERS.get(form_section)
        if handler_info is not None:
            setattr(sac, handler_info["field_name"], audit_data)
            sac.save()

    # this is marked as csrf_exempt to enable by-hand testing via tools like Postman. Should be removed when the frontend form is implemented!
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ExcelFileHandlerView, self).dispatch(*args, **kwargs)

    def post(self, request, *_args, **kwargs):
        """
        Handle Excel file upload:
        validate Excel, validate data, verify SAC exists, redirect.
        """
        try:
            report_id = kwargs["report_id"]

            form_section = kwargs["form_section"]

            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            file = request.FILES["FILES"]

            excel_file = self._create_excel_file(file, sac.id, form_section)

            excel_file.save()

            audit_data = self._extract_and_validate_data(form_section, excel_file)

            self._save_audit_data(sac, form_section, audit_data)

            return redirect("/")

        except SingleAuditChecklist.DoesNotExist as err:
            logger.warning("no SingleAuditChecklist found with report ID %s", report_id)
            raise PermissionDenied() from err
        except ValidationError as err:
            # The good error, where bad rows/columns are sent back in the request.
            # These come back as tuples:
            # [(col1, row1, field1, link1, help-text1), (col2, row2, ...), ...]
            logger.warning("%s Excel upload failed validation: %s", form_section, err)
            return JsonResponse({"errors": list(err), "type": "error_row"}, status=400)
        except MultiValueDictKeyError as err:
            logger.warning("No file found in request")
            raise BadRequest() from err
        except KeyError as err:
            logger.warning("Field error. Field: %s", err)
            return JsonResponse({"errors": str(err), "type": "error_field"}, status=400)
        except ExcelExtractionError as err:
            if err.error_key == UNKNOWN_WORKBOOK:
                return JsonResponse(
                    {"errors": str(err), "type": UNKNOWN_WORKBOOK}, status=400
                )
            raise JsonResponse({"errors": list(err), "type": "error_row"}, status=400)
        except LateChangeError:
            logger.warning("Attempted late change.")
            return JsonResponse(
                {
                    "errors": "Access denied. Further changes to audits that have been marked ready for certification are not permitted.",
                    "type": "no_late_changes",
                },
                status=400,
            )


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


class CrossValidationView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }
            return render(
                request, "audit/cross-validation/cross-validation.html", context
            )
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            errors = sac.validate_full()

            context = {"report_id": report_id, "errors": errors}

            return render(
                request, "audit/cross-validation/cross-validation-results.html", context
            )

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class ReadyForCertificationView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            context = {
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }
            return render(
                request, "audit/cross-validation/ready-for-certification.html", context
            )
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            errors = sac.validate_full()
            if not errors:
                sac.transition_to_ready_for_certification()
                sac.save()
                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

            context = {"report_id": report_id, "errors": errors}
            return render(
                request, "audit/cross-validation/cross-validation-results.html", context
            )

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class AuditorCertificationStep1View(CertifyingAuditorRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            initial = {
                "AuditorCertificationStep1Session": request.session.get(
                    "AuditorCertificationStep1Session", None
                )
            }
            form = AuditorCertificationStep1Form(request.POST or None, initial=initial)
            context = {
                "auditee_uei": sac.auditee_uei,
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "submission_status": sac.submission_status,
                "form": form,
            }
            return render(request, "audit/auditor-certification-step-1.html", context)

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            initial = {
                "AuditorCertificationStep1Session": request.session.get(
                    "AuditorCertificationStep1Session", None
                )
            }
            form = AuditorCertificationStep1Form(request.POST or None, initial=initial)
            context = {
                "auditee_uei": sac.auditee_uei,
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }

            if form.is_valid():
                # Save to session. Retrieved and saved after step 2.
                request.session["AuditorCertificationStep1Session"] = form.cleaned_data
                return redirect(
                    reverse("audit:AuditorCertificationConfirm", args=[report_id])
                )

            context["form"] = form
            return render(request, "audit/auditor-certification-step-1.html", context)

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class AuditorCertificationStep2View(CertifyingAuditorRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            initial = {
                "AuditorCertificationStep2Session": request.session.get(
                    "AuditorCertificationStep2Session", None
                )
            }
            form = AuditorCertificationStep2Form(request.POST or None, initial=initial)

            # Suggests a load/reload on step 2, which means we don't have step 1 session information.
            # Send them back.
            form1_cleaned = request.session.get(
                "AuditorCertificationStep1Session", None
            )
            if form1_cleaned is None:
                return redirect(reverse("audit:AuditorCertification", args=[report_id]))

            context = {
                "auditee_uei": sac.auditee_uei,
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "submission_status": sac.submission_status,
                "form": form,
            }
            return render(request, "audit/auditor-certification-step-2.html", context)

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            form1_cleaned = request.session.get(
                "AuditorCertificationStep1Session", None
            )
            form2 = AuditorCertificationStep2Form(request.POST or None)

            context = {
                "auditee_uei": sac.auditee_uei,
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }

            if form2.is_valid():
                form_cleaned = {
                    "auditor_certification": form1_cleaned,
                    "auditor_signature": form2.cleaned_data,
                }
                form_cleaned["auditor_signature"][
                    "auditor_certification_date_signed"
                ] = form_cleaned["auditor_signature"][
                    "auditor_certification_date_signed"
                ].strftime(
                    "%d/%m/%Y"
                )
                auditor_certification = sac.auditor_certification or {}
                auditor_certification.update(form_cleaned)
                validated = validate_auditor_certification_json(auditor_certification)
                sac.auditor_certification = validated
                sac.transition_to_auditor_certified()
                sac.save()
                logger.info("Auditor certification saved.", auditor_certification)
                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

            context["form"] = form2
            return render(request, "audit/auditor-certification-step-2.html", context)

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class AuditeeCertificationStep1View(CertifyingAuditeeRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            initial = {
                "AuditeeCertificationStep1Session": request.session.get(
                    "AuditeeCertificationStep1Session", None
                )
            }
            form = AuditeeCertificationStep1Form(request.POST or None, initial=initial)
            context = {
                "auditee_uei": sac.auditee_uei,
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "submission_status": sac.submission_status,
                "form": form,
            }
            return render(request, "audit/auditee-certification-step-1.html", context)

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            initial = {
                "AuditeeCertificationStep1Session": request.session.get(
                    "AuditeeCertificationStep1Session", None
                )
            }
            form = AuditeeCertificationStep1Form(request.POST or None, initial=initial)
            context = {
                "auditee_uei": sac.auditee_uei,
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }

            if form.is_valid():
                # Save to session. Retrieved and saved after step 2.
                request.session["AuditeeCertificationStep1Session"] = form.cleaned_data
                return redirect(
                    reverse("audit:AuditeeCertificationConfirm", args=[report_id])
                )

            context["form"] = form
            return render(request, "audit/auditee-certification-step-1.html", context)

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class AuditeeCertificationStep2View(CertifyingAuditeeRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            initial = {
                "AuditeeCertificationStep2Session": request.session.get(
                    "AuditeeCertificationStep2Session", None
                )
            }
            form = AuditeeCertificationStep2Form(request.POST or None, initial=initial)

            # Suggests a load/reload on step 2, which means we don't have step 1 session information.
            # Send them back.
            form1_cleaned = request.session.get(
                "AuditeeCertificationStep1Session", None
            )
            if form1_cleaned is None:
                return redirect(reverse("audit:AuditeeCertification", args=[report_id]))

            context = {
                "auditee_uei": sac.auditee_uei,
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "submission_status": sac.submission_status,
                "form": form,
            }
            return render(request, "audit/auditee-certification-step-2.html", context)

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            form1_cleaned = request.session.get(
                "AuditeeCertificationStep1Session", None
            )
            form2 = AuditeeCertificationStep2Form(request.POST or None)

            context = {
                "auditee_uei": sac.auditee_uei,
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "submission_status": sac.submission_status,
            }

            if form2.is_valid():
                form_cleaned = {
                    "auditee_certification": form1_cleaned,
                    "auditee_signature": form2.cleaned_data,
                }
                form_cleaned["auditee_signature"][
                    "auditee_certification_date_signed"
                ] = form_cleaned["auditee_signature"][
                    "auditee_certification_date_signed"
                ].strftime(
                    "%d/%m/%Y"
                )
                auditee_certification = sac.auditee_certification or {}
                auditee_certification.update(form_cleaned)
                validated = validate_auditee_certification_json(auditee_certification)
                sac.auditee_certification = validated
                sac.transition_to_auditee_certified()
                sac.save()
                logger.info("Auditee certification saved.", auditee_certification)
                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

            context["form"] = form2
            return render(request, "audit/auditee-certification-step-2.html", context)

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

            return redirect(reverse("audit:MySubmissions"))

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class SubmissionProgressView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    """
    Display information about and the current status of the sections of the submission,
    including links to the pages for the sections.

    The following sections have three states, rather than two:

    +   Additionai UEIs
    +   Additionai EINs
    +   Secondary Auditors

    The states are:

    +   hidden
    +   incomplete
    +   complete

    In each case, they are hidden if the corresponding question in the General
    Information form has been answered with a negative response.
    """

    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            try:
                sar = SingleAuditReportFile.objects.filter(sac_id=sac.id).latest(
                    "date_created"
                )
            except SingleAuditReportFile.DoesNotExist:
                sar = None

            shaped_sac = sac_validation_shape(sac)
            subcheck = submission_progress_check(shaped_sac, sar, crossval=False)

            context = {
                "single_audit_checklist": {
                    "created": True,
                    "created_date": sac.date_created,
                    "created_by": sac.submitted_by,
                    "completed": False,
                    "completed_date": None,
                    "completed_by": None,
                },
                "pre_submission_validation": {
                    "completed": sac.submission_status == "ready_for_certification",
                    "completed_date": None,
                    "completed_by": None,
                    # We want the user to always be able to run this check:
                    "enabled": True,
                },
                "certification": {
                    "auditor_certified": bool(sac.auditor_certification),
                    "auditor_enabled": sac.submission_status
                    == "ready_for_certification",
                    "auditee_certified": bool(sac.auditee_certification),
                    "auditee_enabled": sac.submission_status == "auditor_certified",
                },
                "submission": {
                    "completed": sac.submission_status == "submitted",
                    "completed_date": None,
                    "completed_by": None,
                    "enabled": sac.submission_status == "auditee_certified",
                },
                "report_id": report_id,
                "auditee_name": sac.auditee_name,
                "auditee_uei": sac.auditee_uei,
                "user_provided_organization_type": sac.user_provided_organization_type,
            }
            context = context | subcheck

            return render(
                request, "audit/submission_checklist/submission-checklist.html", context
            )
        except SingleAuditChecklist.DoesNotExist as err:
            raise PermissionDenied("You do not have access to this audit.") from err


class AuditInfoFormView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            current_info = {}
            if sac.audit_information:
                current_info = {
                    "cleaned_data": {
                        "gaap_results": sac.audit_information.get("gaap_results"),
                        "sp_framework_basis": sac.audit_information.get(
                            "sp_framework_basis"
                        ),
                        "is_sp_framework_required": sac.audit_information.get(
                            "is_sp_framework_required"
                        ),
                        "sp_framework_opinions": sac.audit_information.get(
                            "sp_framework_opinions"
                        ),
                        "is_going_concern_included": sac.audit_information.get(
                            "is_going_concern_included"
                        ),
                        "is_internal_control_deficiency_disclosed": sac.audit_information.get(
                            "is_internal_control_deficiency_disclosed"
                        ),
                        "is_internal_control_material_weakness_disclosed": sac.audit_information.get(
                            "is_internal_control_material_weakness_disclosed"
                        ),
                        "is_material_noncompliance_disclosed": sac.audit_information.get(
                            "is_material_noncompliance_disclosed"
                        ),
                        "is_aicpa_audit_guide_included": sac.audit_information.get(
                            "is_aicpa_audit_guide_included"
                        ),
                        "dollar_threshold": sac.audit_information.get(
                            "dollar_threshold"
                        ),
                        "is_low_risk_auditee": sac.audit_information.get(
                            "is_low_risk_auditee"
                        ),
                        "agencies": sac.audit_information.get("agencies"),
                    }
                }

            context = self._get_context(sac, current_info)

            return render(request, "audit/audit-info-form.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
        except Exception as e:
            logger.info("Enexpected error in AuditInfoFormView get.\n", e)
            raise BadRequest()

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            form = AuditInfoForm(request.POST)

            if form.is_valid():
                form.clean_booleans()

                audit_information = sac.audit_information or {}
                audit_information.update(form.cleaned_data)
                validated = validate_audit_information_json(audit_information)
                sac.audit_information = validated
                sac.save()
                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        logger.warn(f"ERROR in field {field} : {error}")

                form.clean_booleans()
                context = self._get_context(sac, form)
                return render(request, "audit/audit-info-form.html", context)

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
        except Exception as e:
            logger.info("Enexpected error in AuditInfoFormView post.\n", e)
            raise BadRequest()

    def _get_context(self, sac, form):
        context = {
            "auditee_name": sac.auditee_name,
            "report_id": sac.report_id,
            "auditee_uei": sac.auditee_uei,
            "user_provided_organization_type": sac.user_provided_organization_type,
            "agency_names": AGENCY_NAMES,
            "gaap_results": GAAP_RESULTS,
            "sp_framework_basis": SP_FRAMEWORK_BASIS,
            "sp_framework_opinions": SP_FRAMEWORK_OPINIONS,
        }
        for field, value in context.items():
            logger.warn(f"{field}:{value}")
        context.update(
            {
                "form": form,
            }
        )
        return context
