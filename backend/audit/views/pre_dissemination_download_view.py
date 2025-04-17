from django.http import HttpResponse, Http404
from django.shortcuts import redirect
from django.views.generic import View

from dissemination.file_downloads import get_download_url, get_filename
from dissemination.report_generation.audit_summary_reports import (
    generate_audit_summary_report,
)
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import Audit


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

        audit = Audit.objects.get(report_id=report_id)
        if not audit:
            raise Http404(f"No audit found for report {report_id}")

        filename, workbook_bytes = generate_audit_summary_report(
            report_ids=[report_id], include_private=True, pre_submission=True
        )

        response = HttpResponse(
            workbook_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"

        return response
