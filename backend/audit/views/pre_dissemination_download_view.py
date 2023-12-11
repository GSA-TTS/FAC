from django.shortcuts import get_object_or_404, redirect
from django.views.generic import View

from audit.file_downloads import get_download_url, get_filename
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
