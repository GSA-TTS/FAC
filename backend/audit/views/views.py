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
    SubmissionEvent,
)
from audit.models.models import STATUS
from audit.models.viewflow import sac_transition
from audit.intakelib.exceptions import ExcelExtractionError
from audit.validators import (
    validate_auditee_certification_json,
    validate_auditor_certification_json,
)
from audit.utils import FORM_SECTION_HANDLERS

from dissemination.remove_workbook_artifacts import remove_workbook_artifacts
from dissemination.file_downloads import get_download_url, get_filename
from dissemination.models import General

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)


# 2023-08-22 DO NOT ADD ANY FURTHER CODE TO THIS FILE; ADD IT IN viewlib AS WITH UploadReportView


def _friendly_status(status):
    return dict(SingleAuditChecklist.STATUS_CHOICES)[status]


def verify_status(status):
    """
    Decorator to be applied to view request methods (i.e. get, post) to verify
    that the submission is in the correct state before allowing the user to
    proceed. An incorrect status usually happens via direct URL access. If the
    given status does not match the submission's, it will redirect them back to
    the submission progress page.
    """

    def decorator_verify_status(request_method):
        def verify(view, request, *args, **kwargs):
            report_id = kwargs["report_id"]

            try:
                sac = SingleAuditChecklist.objects.get(report_id=report_id)
            except SingleAuditChecklist.DoesNotExist:
                raise PermissionDenied("You do not have access to this audit.")

            # Return to checklist, the Audit is not in the correct state.
            if sac.submission_status != status:
                logger.warning(
                    f"Expected submission status {status} but it's currently {sac.submission_status}"
                )
                return redirect(f"/audit/submission-progress/{sac.report_id}")
            else:
                return request_method(view, request, *args, **kwargs)

        return verify

    return decorator_verify_status


class MySubmissions(LoginRequiredMixin, generic.View):
    redirect_field_name = "Home"

    def get(self, request, *args, **kwargs):
        template_name = "audit/my_submissions.html"
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
        sac_ids = [access.sac.id for access in accesses]
        data = SingleAuditChecklist.objects.filter(
            Q(id__in=sac_ids) & ~Q(submission_status=STATUS.FLAGGED_FOR_REMOVAL)
        ).values(
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

    def _save_audit_data(self, sac, form_section, audit_data):
        handler_info = FORM_SECTION_HANDLERS.get(form_section)
        if handler_info is not None:
            setattr(sac, handler_info["field_name"], audit_data)
            sac.save()

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

            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            file = request.FILES["FILES"]

            excel_file = self._create_excel_file(file, sac.id, form_section)

            excel_file.save(
                event_user=request.user, event_type=self._event_type(form_section)
            )

            auditee_uei = None
            if (
                sac.general_information is not None
                and "auditee_uei" in sac.general_information
            ):
                auditee_uei = sac.general_information["auditee_uei"]

            audit_data = self._extract_and_validate_data(
                form_section, excel_file, auditee_uei
            )

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

            errors = sac.validate_full()
            if not errors:
                sac_transition(
                    request, sac, transition_to=STATUS.READY_FOR_CERTIFICATION
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
                if sac_transition(request, sac, transition_to=STATUS.AUDITOR_CERTIFIED):
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
                if sac_transition(request, sac, transition_to=STATUS.AUDITEE_CERTIFIED):
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

            errors = sac.validate_full()
            if errors:
                context = {"report_id": report_id, "errors": errors}

                return render(
                    request,
                    "audit/cross-validation/cross-validation-results.html",
                    context,
                )

            # Only change this value if things work...
            disseminated = "DID NOT DISSEMINATE"

            # BEGIN ATOMIC BLOCK
            with transaction.atomic():
                sac_transition(request, sac, transition_to=STATUS.SUBMITTED)
                disseminated = sac.disseminate()
                # `disseminated` is None if there were no errors.
                if disseminated is None:
                    sac_transition(request, sac, transition_to=STATUS.DISSEMINATED)
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


# 2023-08-22 DO NOT ADD ANY FURTHER CODE TO THIS FILE; ADD IT IN viewlib AS WITH UploadReportView
