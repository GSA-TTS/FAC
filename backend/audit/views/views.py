import logging

from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.db import transaction
from django.db.models import F, Q
from django.db.transaction import TransactionManagementError
from django.core.exceptions import BadRequest, PermissionDenied, ValidationError
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.http import JsonResponse

from audit.fixtures.excel import FORM_SECTIONS, UNKNOWN_WORKBOOK
from audit.forms import (
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
    SubmissionEvent, Audit,
)
from audit.models.constants import FINDINGS_BITMASK, FINDINGS_FIELD_TO_BITMASK, STATUS, STATUS_CHOICES
# from audit.models.models import STATUS
from audit.models.viewflow import sac_transition
from audit.intakelib.exceptions import ExcelExtractionError
from audit.utils import FORM_SECTION_HANDLERS
from audit.validators import (
    validate_auditee_certification_json,
    validate_auditor_certification_json,
)
from audit.verify_status import verify_status

from audit.context import set_sac_to_context
from dissemination.docs import major_program
from dissemination.remove_workbook_artifacts import remove_workbook_artifacts
from dissemination.file_downloads import get_download_url, get_filename
from dissemination.models import General

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)


# 2023-08-22 DO NOT ADD ANY FURTHER CODE TO THIS FILE; ADD IT IN viewlib AS WITH UploadReportView


def _friendly_status(status):
    return dict(STATUS_CHOICES)[status]


class MySubmissions(LoginRequiredMixin, generic.View):
    redirect_field_name = "Home"

    def get(self, request, *args, **kwargs):
        template_name = "audit/audit_submissions/audit_submissions.html"
        new_link = "report_submission"
        edit_link = "audit:EditSubmission"

        submissions = MySubmissions.fetch_my_submissions(request.user)

        data = {"completed_audits": [], "in_progress_audits": []}
        for audit in submissions:
            audit["submission_status"] = _friendly_status(audit["submission_status"])
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

        # TODO: replace this with audit IDs -- commented below.
        sac_ids = [access.sac.id for access in accesses]
        data = Audit.objects.filter(
            Q(id__in=sac_ids) & ~Q(submission_status=STATUS.FLAGGED_FOR_REMOVAL)
        ).values(
            "report_id",
            "submission_status",
            "auditee_uei",
            auditee_name=F("audit__general_information__auditee_name"),
            fiscal_year_end_date=F("audit__general_information__auditee_fiscal_period_end")
        )
        # TODO: 2/25 access audit
        # The values for audit are invalid.
        # audit_ids = [access.audit.id for access in accesses]
        # data = Audit.objects.filter(
        #     Q(id__in=audit_ids) & ~Q(submission_status=STATUS.FLAGGED_FOR_REMOVAL)
        # ).values(
        #     "report_id",
        #     "submission_status",
        #     auditee_uei=F("general_information__auditee_uei"),
        #     auditee_name=F("general_information__auditee_name"),
        #     fiscal_year_end_date=F("general_information__auditee_fiscal_period_end"),
        # )
        return data

class EditSubmission(LoginRequiredMixin, generic.View):
    redirect_field_name = "Home"

    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        return redirect(reverse("singleauditchecklist", args=[report_id]))


class ExcelFileHandlerView(SingleAuditChecklistAccessRequiredMixin, generic.View):
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

    def _event_type(self, form_section):
        return {
            FORM_SECTIONS.ADDITIONAL_EINS: SubmissionEvent.EventType.ADDITIONAL_EINS_UPDATED,
            FORM_SECTIONS.ADDITIONAL_UEIS: SubmissionEvent.EventType.ADDITIONAL_UEIS_UPDATED,
            FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: SubmissionEvent.EventType.CORRECTIVE_ACTION_PLAN_UPDATED,
            FORM_SECTIONS.FEDERAL_AWARDS: SubmissionEvent.EventType.FEDERAL_AWARDS_UPDATED,
            FORM_SECTIONS.FINDINGS_TEXT: SubmissionEvent.EventType.FEDERAL_AWARDS_AUDIT_FINDINGS_TEXT_UPDATED,
            FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: SubmissionEvent.EventType.FINDINGS_UNIFORM_GUIDANCE_UPDATED,
            FORM_SECTIONS.NOTES_TO_SEFA: SubmissionEvent.EventType.NOTES_TO_SEFA_UPDATED,
            FORM_SECTIONS.SECONDARY_AUDITORS: SubmissionEvent.EventType.SECONDARY_AUDITORS_UPDATED,
        }[form_section]

    def _extract_and_validate_data(self, form_section, excel_file, auditee_uei):
        handler_info = FORM_SECTION_HANDLERS.get(form_section)
        if handler_info is None:
            logger.warning("No form section found with name %s", form_section)
            raise BadRequest()
        audit_data = handler_info["extractor"](excel_file.file, auditee_uei=auditee_uei)
        validator = handler_info.get("validator")
        if validator is not None and callable(validator):
            validator(audit_data)
        return audit_data

    def _save_audit_data(self, sac, form_section, audit_data, user=None):
        handler_info = FORM_SECTION_HANDLERS.get(form_section)
        if handler_info is not None:
            setattr(sac, handler_info["field_name"], audit_data)
            sac.save()

            #TODO Audit Rework
            # remove try/except once we are ready to deprecate SAC.
            try:
                audit = Audit.objects.get(report_id=sac.report_id)
                audit_update = FORM_SECTION_HANDLERS.get(form_section)["audit_object"](audit_data)
                audit.audit.update(audit_update)
                audit.save(
                    event_user=user,
                    event_type=self._event_type(form_section),
                )
            except Audit.DoesNotExist:
                pass

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(ExcelFileHandlerView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Given a report ID and form section, redirect the caller to a download URL for the associated Excel file (if one exists)
        """
        try:
            report_id = kwargs["report_id"]
            form_section = kwargs["form_section"]

            filename = get_filename(report_id, form_section)
            download_url = get_download_url(filename)

            return redirect(download_url)
        except SingleAuditChecklist.DoesNotExist as err:
            logger.warning("no SingleAuditChecklist found with report ID %s", report_id)
            raise PermissionDenied() from err

    def post(self, request, *_args, **kwargs):
        """
        Handle Excel file upload:
        validate Excel, validate data, verify SAC exists, redirect.
        """
        try:
            report_id = kwargs["report_id"]
            form_section = kwargs["form_section"]
            file = request.FILES["FILES"]
            auditee_uei = None

            # TODO: 2/25 access audit
            # When we are ready to transition SAC -> Audit:
            # 1 - Remove this try block.
            # 2 - Within the "Except" block, uncomment all relevant lines.
            # 3 - Switch the SingleAuditChecklist.DoesNotExist -> Audit.DoesNotExist in the outer Except block.
            try:
                audit = Audit.objects.get(report_id=report_id)

                excel_file = self._create_excel_file(file, sac.id, form_section)

                if (
                    audit.audit['general_information'] is not None
                    and "auditee_uei" in audit.audit['general_information']
                ):
                    auditee_uei = audit.audit.get('general_information', {}).get("auditee_uei", None)
                with set_sac_to_context(sac):
                    audit_data = self._extract_and_validate_data(
                        form_section, excel_file, auditee_uei
                    )
                    excel_file.save(
                        event_user=request.user, event_type=self._event_type(form_section)
                    )
                    self._save_audit_data(sac, form_section, audit_data, request.user)

                    return redirect("/")

            except Audit.DoesNotExist:

                # TODO: 2/25 access audit
                # uncomment the lines below when we switch SAC -> audit.

                sac = SingleAuditChecklist.objects.get(report_id=report_id)
                # audit = Audit.objects.get(report_id=report_id)

                excel_file = self._create_excel_file(file, sac.id, form_section)

                if (
                    sac.general_information is not None
                    and "auditee_uei" in sac.general_information
                    # audit.audit['general_information'] is not None
                    # and "auditee_uei" in audit.audit['general_information']
                ):
                    auditee_uei = sac.general_information["auditee_uei"]
                    # auditee_uei = audit.audit.get('general_information', {}).get("auditee_uei", None)
                with set_sac_to_context(sac):
                    audit_data = self._extract_and_validate_data(
                        form_section, excel_file, auditee_uei
                    )
                    excel_file.save(
                        event_user=request.user, event_type=self._event_type(form_section)
                    )
                    self._save_audit_data(sac, form_section, audit_data, request.user)

                    return redirect("/")

        # TODO: 2/25 access audit
        # Switch this model with "Audit" when we switch SAC -> audit.
        except SingleAuditChecklist.DoesNotExist as err:
            logger.warning("no SAC found with report ID %s", report_id)
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
    def post(self, request, *args, **kwargs):
        try:
            report_id = kwargs["report_id"]

            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            file = request.FILES["FILES"]

            sar_file = SingleAuditReportFile(
                **{"file": file, "filename": "temp", "sac_id": sac.id}
            )

            sar_file.full_clean()
            sar_file.save(
                event_user=request.user,
                event_type=SubmissionEvent.EventType.AUDIT_REPORT_PDF_UPDATED,
            )

            return redirect("/")

        except MultiValueDictKeyError:
            logger.warn("No file found in request")
            raise BadRequest()


class CrossValidationView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    @verify_status(STATUS.IN_PROGRESS)
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

    @verify_status(STATUS.IN_PROGRESS)
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
    @verify_status(STATUS.IN_PROGRESS)
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

    @verify_status(STATUS.IN_PROGRESS)
    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            # TODO: 2/25 access audit
            # remove try/except once we are ready to deprecate SAC.
            try:
                audit = Audit.objects.get(report_id=report_id)
            except Audit.DoesNotExist:
                audit = None
            errors = sac.validate_full()
            if not errors:
                sac_transition(
                    request, sac, audit=audit, transition_to=STATUS.READY_FOR_CERTIFICATION
                )
                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))
            else:
                context = {"report_id": report_id, "errors": errors}
                return render(
                    request,
                    "audit/cross-validation/cross-validation-results.html",
                    context,
                )

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class AuditorCertificationStep1View(CertifyingAuditorRequiredMixin, generic.View):
    @verify_status(STATUS.READY_FOR_CERTIFICATION)
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

            # Return to checklist, the Audit is not in the correct state.
            if sac.submission_status != STATUS.READY_FOR_CERTIFICATION:
                return redirect(f"/audit/submission-progress/{sac.report_id}")

            return render(request, "audit/auditor-certification-step-1.html", context)

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    @verify_status(STATUS.READY_FOR_CERTIFICATION)
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

            # Return to checklist, the Audit is not in the correct state.
            if sac.submission_status != STATUS.READY_FOR_CERTIFICATION:
                return redirect(f"/audit/submission-progress/{sac.report_id}")

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
    @verify_status(STATUS.READY_FOR_CERTIFICATION)
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

            # Return to checklist, the Audit is not in the correct state.
            if sac.submission_status != STATUS.READY_FOR_CERTIFICATION:
                return redirect(f"/audit/submission-progress/{sac.report_id}")

            return render(request, "audit/auditor-certification-step-2.html", context)

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    @verify_status(STATUS.READY_FOR_CERTIFICATION)
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

            # Return to checklist, the Audit is not in the correct state.
            if sac.submission_status != STATUS.READY_FOR_CERTIFICATION:
                return redirect(f"/audit/submission-progress/{sac.report_id}")

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
                    "%Y-%m-%d"
                )
                auditor_certification = sac.auditor_certification or {}
                auditor_certification.update(form_cleaned)
                validated = validate_auditor_certification_json(auditor_certification)
                sac.auditor_certification = validated
                # TODO: 2/25 access audit
                # remove try/except once we are ready to deprecate SAC.
                try:
                    audit = Audit.objects.get(report_id=report_id)
                    audit.audit.update({"auditor_certification": validated})
                except Audit.DoesNotExist:
                    audit = None
                if sac_transition(request, sac, audit=audit, transition_to=STATUS.AUDITOR_CERTIFIED):
                    logger.info("Auditor certification saved.", auditor_certification)
                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

            context["form"] = form2
            return render(request, "audit/auditor-certification-step-2.html", context)

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class AuditeeCertificationStep1View(CertifyingAuditeeRequiredMixin, generic.View):
    @verify_status(STATUS.AUDITOR_CERTIFIED)
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

    @verify_status(STATUS.AUDITOR_CERTIFIED)
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
    @verify_status(STATUS.AUDITOR_CERTIFIED)
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

    @verify_status(STATUS.AUDITOR_CERTIFIED)
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
                    "%Y-%m-%d"
                )
                auditee_certification = sac.auditee_certification or {}
                auditee_certification.update(form_cleaned)
                validated = validate_auditee_certification_json(auditee_certification)
                sac.auditee_certification = validated
                # TODO: 2/25 access audit
                # remove try/except once we are ready to deprecate SAC.
                try:
                    audit = Audit.objects.get(report_id=report_id)
                    audit.audit.update({"auditee_certification": validated })
                except Audit.DoesNotExist:
                    audit = None
                if sac_transition(request, sac, audit=audit, transition_to=STATUS.AUDITEE_CERTIFIED):
                    logger.info("Auditee certification saved.", auditee_certification)
                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

            context["form"] = form2
            return render(request, "audit/auditee-certification-step-2.html", context)

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class CertificationView(CertifyingAuditeeRequiredMixin, generic.View):
    @verify_status(STATUS.AUDITOR_CERTIFIED)
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

    @verify_status(STATUS.AUDITOR_CERTIFIED)
    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            sac.save()

            return redirect(reverse("audit:MySubmissions"))

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")


class SubmissionView(CertifyingAuditeeRequiredMixin, generic.View):
    @verify_status(STATUS.AUDITEE_CERTIFIED)
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

    @verify_status(STATUS.AUDITEE_CERTIFIED)
    def post(self, request, *args, **kwargs):
        # RACE HAZARD WARNING
        # It is possible for a user to enter the submission multiple times,
        # from multiple FAC instances. This race hazard is documented in
        # backend/audit/views/README-fac-views-race-hazard-postmortem.md
        report_id = kwargs["report_id"]
        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            # TODO: 2/25 access audit
            # remove try/except once we are ready to deprecate SAC.
            try:
                audit = Audit.objects.get(report_id=report_id)
            except Audit.DoesNotExist:
                audit = None
            errors = sac.validate_full()
            if errors:
                context = {"report_id": report_id, "errors": errors}

                return render(
                    request,
                    "audit/cross-validation/cross-validation-results.html",
                    context,
                )

              ## TODO!~!!
            # Only change this value if things work...
            disseminated = "DID NOT DISSEMINATE"

            # BEGIN ATOMIC BLOCK
            with transaction.atomic():
                sac_transition(request, sac, audit=audit, transition_to=STATUS.SUBMITTED)
                disseminated = sac.disseminate()
                _compute_additional_audit_fields(audit, sac)
                # `disseminated` is None if there were no errors.
                if disseminated is None:
                    sac_transition(request, sac, audit=audit, transition_to=STATUS.DISSEMINATED)
            # END ATOMIC BLOCK

            # IF THE DISSEMINATION SUCCEEDED
            # `disseminated` is None if there were no errors.
            if disseminated is None:
                # Remove workbook artifacts after the report has been disseminated.
                # We do this outside of the atomic block. No race between
                # two instances of the FAC should be able to get to this point.
                # If we do, something will fail.
                remove_workbook_artifacts(sac)

            # IF THE DISSEMINATION FAILED
            # If disseminated has a value, it is an error
            # object returned from `sac.disseminate()`
            if disseminated is not None:
                logger.info(
                    "{} is a `not None` value report_id[{}] for `disseminated`".format(
                        report_id, disseminated
                    )
                )

            return redirect(reverse("audit:MySubmissions"))

        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")
        except TransactionManagementError:
            # ORIGINAL COMMENT
            # This is most likely the result of a race condition, where the user hits
            # the submit button multiple times and the requests get round-robined to
            # different instances, and the second attempt tries to insert an existing
            # report_id into the dissemination.General table.
            # Our assumption is that the first request succeeded (otherwise there
            # wouldn't be an entry with that report_id to cause the error), and that we
            # should log this but not report it to the user.
            # See https://github.com/GSA-TTS/FAC/issues/3347
            # UPDATED 2024-09-13
            # We have not been able to trigger this error in the most recent race
            # debugging. However, that does not mean it is impossible.
            # Therefore, leaving this exception handler in place.
            logger.info("IntegrityError on disseminating report_id: %s", report_id)
            if General.objects.get(report_id=sac.report_id):
                return redirect(reverse("audit:MySubmissions"))
            raise

# TODO:
#    1) We'll want to calculate the cog/oversite for the audit same way as sac, for now just use the sac one
#    2) Move this somewhere else... this file huge
def _compute_additional_audit_fields(audit, sac):
    general_information = audit.get("general_information", {})
    audit_year, fy_end_month, _ = general_information.get("auditee_fiscal_period_end",
                                                          "1900-01-01").split("-")

    cognizant_agency = sac.cognizant_agency
    oversight_agency = sac.oversight_agency

    is_public = general_information.get("user_provided_organization_type",
                                        "") != "tribal" or \
                audit.get("tribal_data_consent", {}).get(
                    "is_tribal_information_authorized_to_be_public", True)
    awards_indexes = _index_awards(audit)
    findings_indexes = _index_findings(audit)
    general_indexes = _index_general(audit)

    audit.update({
        "audit_year": audit_year,
        "cognizant_agency": cognizant_agency,
        "oversight_agency": oversight_agency,
        "fy_end_month": fy_end_month,
        "is_public": is_public,

        "search_indexes": {
            **findings_indexes,
            **awards_indexes,
            **general_indexes
        }})
    audit.save()

def _index_findings(audit_data):
    findings = 0
    compliance_requirements = set()
    for finding in audit_data.get("findings_uniform_guidance", []):
        for mask in FINDINGS_FIELD_TO_BITMASK:
            if finding.get(mask.field, "N") == "Y":
                findings |= mask.mask
        if finding.get("finding", {}).get("repeat_prior_reference", "N") == "Y":
            findings |= FINDINGS_BITMASK.REPEAT_FINDING

        compliance_requirement = finding.get("program", {}).get("compliance_requirement", "")
        compliance_requirements.add(compliance_requirement)

    return {
        "findings_summary": findings,
        "compliance_requirements": list(compliance_requirements),
    }

def _index_awards(audit_data):
    """
    Method for pulling out all the data from awards that we search on, to improve
    search performance.
    """
    program_names = []
    passthrough_names = set()
    agency_prefixes = set()
    agency_extensions = set()
    has_direct_funding = False
    has_indirect_funding = False
    is_major_program = False

    for award in audit_data.get("federal_awards", {}).get("awards", []):
        program = award.get("program", {})
        if program.get("program_name", ""):
            program_names.append(award["program"]["program_name"])
        if program.get("is_major", "N") == "Y":
            is_major_program = True
        agency_prefixes.add(program.get("federal_agency_prefix", ""))
        agency_extensions.add(program.get("three_digit_extension", ""))

        if award.get("direct_or_indirect_award", {}).get("is_direct", "") == 'Y':
            has_direct_funding = True
        elif award.get("direct_or_indirect_award", {}).get("is_direct", "") == 'N':
            has_indirect_funding = True
        passthrough_names.update([entity.get("passthrough_name", None) for entity in
                                  award.get("direct_or_indirect_award",
                                            {}).get("entities", [])])

    return {
        "program_names": program_names,
        "has_direct_funding": has_direct_funding,
        "has_indirect_funding": has_indirect_funding,
        "is_major_program": is_major_program,
        "passthrough_names": list(passthrough_names),
        "agency_extensions": list(agency_extensions),
        "agency_prefixes": list(agency_prefixes)
    }

def _index_general(audit_data):

    general_information = audit_data.get("general_information", {})

    search_names = set()
    general_fields = ["auditee_contact_name", "auditee_email", "auditee_name", "auditor_contact_name", "auditor_email", "auditor_firm_name"]
    for field in general_fields:
        search_names.add(general_information.get(field, ""))

    # Also search over certification
    auditee_certify_name = audit_data.get(
        "auditee_certification", {}).get(
        "auditee_signature",{}).get(
        "auditee_name", "")
    auditor_certify_name = audit_data.get(
        "auditor_certification", {}).get(
        "auditor_signature",{}).get(
        "auditor_name", "")

    search_names.add(auditee_certify_name)
    search_names.add(auditor_certify_name)

    return {
        "search_names": list(search_names),
    }

# 2023-08-22 DO NOT ADD ANY FURTHER CODE TO THIS FILE; ADD IT IN viewlib AS WITH UploadReportView
