from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View

from audit.intake_to_dissemination import IntakeToDissemination
from dissemination.file_downloads import get_download_url, get_filename
from dissemination.summary_reports import generate_presubmission_report
from audit.mixins import (
    SingleAuditChecklistAccessRequiredMixin,
)
from audit.models import SingleAuditChecklist


class PredisseminationXlsxDownloadView(SingleAuditChecklistAccessRequiredMixin, View):
    def get(self, request, report_id, file_type):
        sac = get_object_or_404(SingleAuditChecklist, report_id=report_id)
        filename = get_filename(sac, file_type)

        return redirect(get_download_url(filename))


class PredisseminationPdfDownloadView(SingleAuditChecklistAccessRequiredMixin, View):
    def get(self, request, report_id):
        sac = get_object_or_404(SingleAuditChecklist, report_id=report_id)
        filename = get_filename(sac, "report")

        return redirect(get_download_url(filename))


class PredisseminationSummaryReportDownloadView(
    SingleAuditChecklistAccessRequiredMixin, View
):
    def get(self, request, report_id):
        sac = get_object_or_404(SingleAuditChecklist, report_id=report_id)

        intake_to_dissem = IntakeToDissemination(
            sac, mode=IntakeToDissemination.PRE_CERTIFICATION_REVIEW
        )
        i2d_data = intake_to_dissem.load_all()

        filename = generate_presubmission_report(i2d_data)
        download_url = get_download_url(filename)

        return redirect(download_url)
