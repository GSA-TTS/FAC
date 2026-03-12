import logging

from django.core.exceptions import BadRequest, PermissionDenied, ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse

from audit.forms import UploadReportForm
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    LateChangeError,
    SingleAuditChecklist,
    SingleAuditReportFile,
    Audit,
)
from audit.models.constants import EventType
from dissemination.file_downloads import copy_file

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)

# TODO: Update Post SOC Launch


class PageInput:
    """
    Convenience constructor for page inputs.
    Used in audit/templates/audit/upload-report.html
    """

    def __init__(self, text="", id="", required=True, hint=None):
        self.text = text
        self.id = id
        self.required = required
        self.hint = hint


class UploadReportView(SingleAuditChecklistAccessRequiredMixin, generic.View):
    def page_number_inputs(self) -> list[PageInput]:
        """
        Build the input elements to be passed to the context for use in
        audit/templates/audit/upload-report.html
        """
        return [
            PageInput(
                "Financial Statement(s) 2 CFR 200.510(a)", "financial_statements"
            ),
            PageInput(
                "Opinion on Financial Statements 2 CFR 200.515(a)",
                "financial_statements_opinion",
            ),
            PageInput(
                "Schedule of Expenditures of Federal Awards 2 CFR 200.510(b)",
                "schedule_expenditures",
            ),
            PageInput(
                "Opinion or Disclaimer of Opinion on Schedule of Federal Awards 2 CFR 200.515(a)",
                "schedule_expenditures_opinion",
            ),
            PageInput(
                "Uniform Guidance Report on Internal Control 2 CFR 200.515(b)",
                "uniform_guidance_control",
            ),
            PageInput(
                "Uniform Guidance Report on Compliance 2 CFR 200.515(c)",
                "uniform_guidance_compliance",
            ),
            PageInput("GAS Report on Internal Control 2 CFR 200.515(b)", "GAS_control"),
            PageInput(
                "GAS Report on Internal Compliance 2 CFR 200.515(b)", "GAS_compliance"
            ),
            PageInput(
                "Schedule of Findings and Questioned Costs 2 CFR 200.515(d)",
                "schedule_findings",
            ),
            PageInput(
                "Summary Schedule of Prior Audit Findings 2 CFR 200.511(b)",
                "schedule_prior_findings",
                required=False,
                hint="Only required if prior audit findings exist",
            ),
            PageInput(
                "Corrective Action Plan (if findings) 2 CFR 200.511(c)",
                "CAP_page",
                required=False,
                hint="Only required if findings exist",
            ),
        ]

    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            sar = SingleAuditReportFile.objects.filter(sac_id=sac.id)
            if sar.exists():
                sar = sar.latest("date_created")
            current_info = {
                "cleaned_data": getattr(sar, "component_page_numbers", {}),
            }

            previous_report_id = (
                sac.resubmission_meta.get("previous_report_id")
                if sac.resubmission_meta
                else None
            )

            context = {
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "auditee_uei": sac.auditee_uei,
                "user_provided_organization_type": sac.user_provided_organization_type,
                "page_number_inputs": self.page_number_inputs(),
                "already_submitted": True if sar else False,
                "is_resubmission": True if previous_report_id else False,
                "form": current_info,
            }

            return render(request, "audit/upload-report.html", context)
        except SingleAuditChecklist.DoesNotExist as err:
            raise PermissionDenied("You do not have access to this audit.") from err
        except Exception as err:
            logger.error("Enexpected error in UploadReportView get:\n%s", err)
            raise BadRequest() from err

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            # TODO SOT: Switch to `audit`
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            form = UploadReportForm(request.POST, request.FILES)

            previous_report_id = (
                sac.resubmission_meta.get("previous_report_id")
                if sac.resubmission_meta
                else None
            )

            # Standard context always needed on this page
            context = {
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "auditee_uei": sac.auditee_uei,
                "user_provided_organization_type": sac.user_provided_organization_type,
                "page_number_inputs": self.page_number_inputs(),
                "is_resubmission": bool(previous_report_id),
            }

            # Find form errors and return if any exist, then EITHER:
            # 1. For resubmissions that opt in, copy the previous report.
            # 2. For original or updated resubmissions, validate and store as normal.
            if not form.is_valid():
                return render(
                    request, "audit/upload-report.html", context | {"form": form}
                )

            if form.cleaned_data.get("keep_previous_report") and previous_report_id:
                return self._handle_keep_previous_report(
                    request, report_id, previous_report_id, form, context
                )

            return self._handle_new_report(request, report_id, form, context)

        except SingleAuditChecklist.DoesNotExist as err:
            raise PermissionDenied("You do not have access to this audit.") from err
        except LateChangeError:
            return render(request, "audit/no-late-changes.html")
        except Exception as err:
            logger.error("Unexpected error in UploadReportView post:\n %s", err)
            raise BadRequest() from err

    def _handle_keep_previous_report(
        self,
        request: HttpRequest,
        report_id: str,
        previous_report_id: str,
        form: UploadReportForm,
        context: dict,
    ) -> HttpResponse:
        """
        Copy the previous submission's SingleAuditReportFile and PDF to the current resubmission.
        """
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        audit = Audit.objects.find_audit_or_none(report_id)

        try:
            self.copy_previous_report_data(
                previous_report_id=previous_report_id,
                current_sac=sac,
                current_audit=audit,
                request=request,
            )
        except Exception as err:
            logger.error("Unexpected error copying a SingleAuditReportFile: {err}")
            form.add_error(None, f"Unable to copy the previous report: {err}")
            return render(request, "audit/upload-report.html", context | {"form": form})

        return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

    def _handle_new_report(
        self,
        request: HttpRequest,
        report_id: str,
        form: UploadReportForm,
        context: dict,
    ) -> HttpResponse:
        """
        Validate and store a newly uploaded report.
        """
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        audit = Audit.objects.find_audit_or_none(report_id)

        file = request.FILES["upload_report"]
        sar_file = self.reformat_form_data(
            file, form, sac.id, audit.id if audit else None
        )

        try:
            sar_file.full_clean()
            sar_file.save(
                event_user=request.user,
                event_type=EventType.AUDIT_REPORT_PDF_UPDATED,
            )
            self._save_audit(report_id=report_id, sar_file=sar_file, request=request)
        except ValidationError as err:
            for issue in err.error_dict.get("file"):
                form.add_error("upload_report", issue)
            return render(request, "audit/upload-report.html", context | {"form": form})

        return redirect(reverse("audit:SubmissionProgress", args=[report_id]))

    def reformat_form_data(
        self,
        file: UploadedFile,
        form: UploadReportForm,
        sac_id: int,
        audit_id: int | None,
    ) -> SingleAuditReportFile:
        """
        Given the file, form, and report_id, return the formatted SingleAuditReportFile.
        Maps cleaned form data into an object to be passed alongside the file, filename, and report id.
        """
        component_page_numbers = {
            "financial_statements": form.cleaned_data["financial_statements"],
            "financial_statements_opinion": form.cleaned_data[
                "financial_statements_opinion"
            ],
            "schedule_expenditures": form.cleaned_data["schedule_expenditures"],
            "schedule_expenditures_opinion": form.cleaned_data[
                "schedule_expenditures_opinion"
            ],
            "uniform_guidance_control": form.cleaned_data["uniform_guidance_control"],
            "uniform_guidance_compliance": form.cleaned_data[
                "uniform_guidance_compliance"
            ],
            "GAS_control": form.cleaned_data["GAS_control"],
            "GAS_compliance": form.cleaned_data["GAS_compliance"],
            "schedule_findings": form.cleaned_data["schedule_findings"],
            # These two fields are optional on the part of the submitter
            "schedule_prior_findings": form.cleaned_data["schedule_prior_findings"]
            or None,
            "CAP_page": form.cleaned_data["CAP_page"] or None,
        }
        sar_file = SingleAuditReportFile(
            **{
                "component_page_numbers": component_page_numbers,
                "file": file,
                "filename": file.name,
                "sac_id": sac_id,
                "audit_id": audit_id,
            }
        )
        return sar_file

    def copy_previous_report_data(
        self,
        previous_report_id: str,
        current_sac: SingleAuditChecklist,
        current_audit: Audit | None,
        request: HttpRequest,
    ) -> None:
        """
        Copy the SingleAuditReportFile and the associated s3 object from the
        previous submission to the current resubmission.
        """
        previous_sac = SingleAuditChecklist.objects.get(report_id=previous_report_id)
        previous_sar = SingleAuditReportFile.objects.filter(sac=previous_sac).latest(
            "date_created"
        )

        # Copy the S3 object
        source_key = f"singleauditreport/{previous_sac.report_id}.pdf"
        dest_key = f"singleauditreport/{current_sac.report_id}.pdf"
        copy_file(source_key, dest_key)

        # Copy the SingleAuditReportFile row
        new_sar = SingleAuditReportFile(
            file=dest_key,
            filename=f"{current_sac.report_id}.pdf",
            sac=current_sac,
            audit=current_audit,
            component_page_numbers=previous_sar.component_page_numbers,
        )
        new_sar.save(
            event_user=request.user,
            event_type=EventType.AUDIT_REPORT_PDF_UPDATED,
        )

        # Mirror onto the Audit model if it exists
        if current_audit:
            self._save_audit(
                report_id=current_sac.report_id, sar_file=new_sar, request=request
            )

    @staticmethod
    def _save_audit(
        report_id: str,
        sar_file: SingleAuditReportFile,
        request: HttpRequest,
    ) -> None:
        # TODO: Update Post SOC Launch : Delete and move done for linting complexity
        audit = Audit.objects.find_audit_or_none(report_id=report_id)
        if audit:
            audit.audit.update(
                {
                    "file_information": {
                        "filename": sar_file.filename,
                        "pages": sar_file.component_page_numbers,
                    }
                }
            )
            audit.save(
                event_user=request.user,
                event_type=EventType.AUDIT_REPORT_PDF_UPDATED,
            )
