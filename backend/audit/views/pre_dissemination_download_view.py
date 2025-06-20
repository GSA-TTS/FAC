from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View

from audit.intake_to_dissemination import IntakeToDissemination
from dissemination.file_downloads import get_download_url, get_filename
from dissemination.report_generation.audit_summary_reports import (
    generate_audit_summary_report,
)
from dissemination.summary_reports import generate_presubmission_report
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import SingleAuditChecklist, Audit


class PredisseminationXlsxDownloadView(SingleAuditChecklistAccessRequiredMixin, View):
    def get(self, request, report_id, file_type):
        filename = get_filename(report_id, file_type)
        return redirect(get_download_url(filename))


class PredisseminationPdfDownloadView(SingleAuditChecklistAccessRequiredMixin, View):
    def get(self, request, report_id):
        filename = get_filename(report_id, "report")
        return redirect(get_download_url(filename))


class PredisseminationSummaryReportDownloadView(
    SingleAuditChecklistAccessRequiredMixin, View
):
    def get(self, request, report_id):
        sac = get_object_or_404(SingleAuditChecklist, report_id=report_id)

        # TODO SOT: Enable for testing
        # use_audit = request.GET.get("beta", "N") == "Y"
        use_audit = False
        if use_audit:
            get_object_or_404(Audit, report_id=report_id)

        intake_to_dissem = IntakeToDissemination(
            sac, mode=IntakeToDissemination.PRE_CERTIFICATION_REVIEW
        )
        i2d_data = intake_to_dissem.load_all()

        filename, workbook_bytes = (
            generate_presubmission_report(i2d_data)
            if not use_audit
            else generate_audit_summary_report(
                report_ids=[report_id], include_private=True, pre_submission=True
            )
        )
        response = HttpResponse(
            workbook_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"

        return response
