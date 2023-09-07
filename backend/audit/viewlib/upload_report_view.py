import logging

from django.core.exceptions import BadRequest, PermissionDenied
from django.shortcuts import render, redirect
from django.views import generic
from django.urls import reverse

from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import (
    LateChangeError,
    SingleAuditChecklist,
    SingleAuditReportFile,
    SubmissionEvent,
)
from audit.forms import UploadReportForm

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(module)s:%(lineno)d %(message)s"
)
logger = logging.getLogger(__name__)


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
    def page_number_inputs(self):
        """
        Build the input elements to be passed to the context for use in
        audit/templates/audit/upload-report.html
        """
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
            sar = SingleAuditReportFile.objects.filter(sac_id=sac.id).first()

            current_info = {
                "cleaned_data": getattr(sar, "component_page_numbers", {}),
            }

            context = {
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "auditee_uei": sac.auditee_uei,
                "user_provided_organization_type": sac.user_provided_organization_type,
                "page_number_inputs": self.page_number_inputs(),
                "already_submitted": True if sar else False,
                "form": current_info,
            }

            return render(request, "audit/upload-report.html", context)
        except SingleAuditChecklist.DoesNotExist as err:
            raise PermissionDenied("You do not have access to this audit.") from err
        except Exception as err:
            logger.info("Enexpected error in UploadReportView get:\n%s", err)
            raise BadRequest() from err

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            form = UploadReportForm(request.POST, request.FILES)

            if form.is_valid():
                file = request.FILES["upload_report"]

                component_page_numbers = {
                    "financial_statements": form.cleaned_data["financial_statements"],
                    "financial_statements_opinion": form.cleaned_data[
                        "financial_statements_opinion"
                    ],
                    "schedule_expenditures": form.cleaned_data["schedule_expenditures"],
                    "schedule_expenditures_opinion": form.cleaned_data[
                        "schedule_expenditures_opinion"
                    ],
                    "uniform_guidance_control": form.cleaned_data[
                        "uniform_guidance_control"
                    ],
                    "uniform_guidance_compliance": form.cleaned_data[
                        "uniform_guidance_compliance"
                    ],
                    "GAS_control": form.cleaned_data["GAS_control"],
                    "GAS_compliance": form.cleaned_data["GAS_compliance"],
                    "schedule_findings": form.cleaned_data["schedule_findings"],
                    # These two fields are optional on the part of the submitter
                    "schedule_prior_findings": form.cleaned_data[
                        "schedule_prior_findings"
                    ]
                    or None,
                    "CAP_page": form.cleaned_data["CAP_page"] or None,
                }

                sar_file = SingleAuditReportFile(
                    **{
                        "component_page_numbers": component_page_numbers,
                        "file": file,
                        "filename": file.name,
                        "sac_id": sac.id,
                    }
                )

                sar_file.full_clean()
                sar_file.save(
                    event_user=request.user,
                    event_type=SubmissionEvent.EventType.AUDIT_REPORT_PDF_UPDATED,
                )

                # PDF issues can be communicated to the user with form.errors["upload_report"]
                return redirect(reverse("audit:SubmissionProgress", args=[report_id]))
            context = {
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "auditee_uei": sac.auditee_uei,
                "user_provided_organization_type": sac.user_provided_organization_type,
                "page_number_inputs": self.page_number_inputs(),
                "form": form,
            }
            return render(request, "audit/upload-report.html", context)
        except SingleAuditChecklist.DoesNotExist as err:
            raise PermissionDenied("You do not have access to this audit.") from err
        except LateChangeError:
            return render(request, "audit/no-late-changes.html")

        except Exception as err:
            logger.info("Unexpected error in UploadReportView post:\n %s", err)
            raise BadRequest() from err
