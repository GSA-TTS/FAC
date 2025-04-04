import logging
from datetime import timedelta

from audit.models import Audit
from audit.models.constants import STATUS
from config.settings import SUMMARY_REPORT_DOWNLOAD_LIMIT
from dissemination.file_downloads import (
    get_download_url,
    get_filename,
    get_filename_from_audit,
)
from dissemination.forms import AdvancedSearchForm
from dissemination.mixins import ReportAccessRequiredMixin
from dissemination.models import (
    General,
    OneTimeAccess,
)
from dissemination.report_generation.audit_summary_reports import (
    generate_audit_summary_report,
)
from dissemination.searchlib.search_utils import run_search

from dissemination.summary_reports import generate_summary_report
from django.conf import settings
from django.core.exceptions import BadRequest, ValidationError
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import View

from dissemination.views.utils import include_private_results

logger = logging.getLogger(__name__)


class PdfDownloadView(ReportAccessRequiredMixin, View):
    def get(self, request, report_id):
        """
        Given a report_id in the URL, find the relevant PDF in S3 and
        redirect to the download link.
        """
        # only allow PDF downloads for disseminated submissions
        # TODO: Update Post SOC Launch
        get_object_or_404(General, report_id=report_id)

        use_audit = request.GET.get("beta", "N") == "Y"
        if use_audit:
            get_object_or_404(
                Audit, report_id=report_id, submission_status=STATUS.DISSEMINATED
            )

        filename = (
            get_filename_from_audit(report_id, "report")
            if use_audit
            else get_filename(report_id, "report")
        )

        return redirect(get_download_url(filename))


class XlsxDownloadView(ReportAccessRequiredMixin, View):
    def get(self, request, report_id, file_type):
        """
        Given a report_id and workbook section (file_type) in the URL,
        find the relevant XLSX file in S3 and redirect to its download link.
        """
        # only allow xlsx downloads from disseminated submissions
        # TODO: Update Post SOC Launch
        # get_object_or_404(Audit, report_id=report_id, submission_status=STATUS.DISSEMINATED)
        get_object_or_404(General, report_id=report_id)

        use_audit = request.GET.get("beta", "N") == "Y"
        if use_audit:
            get_object_or_404(
                Audit, report_id=report_id, submission_status=STATUS.DISSEMINATED
            )

        filename = (
            get_filename_from_audit(report_id, file_type)
            if use_audit
            else get_filename(report_id, file_type)
        )

        return redirect(get_download_url(filename))


class OneTimeAccessDownloadView(View):
    def get(self, request, uuid):
        """
        Given a one time access UUID:
        - Clear all expired OneTimeAccess objects from the database
        - Query for a OneTimeAccess object with a matching UUID
        - If found
          - Generate an S3 link to the SingleAuditReport PDF associated with the OneTimeAccess object
          - Delete the OneTimeAccess object
          - Redirect to the generated S3 link
        - If not found
          - Return 404
        """
        try:
            # delete all expired OTA objects
            cutoff = timezone.now() - timedelta(
                seconds=settings.ONE_TIME_ACCESS_TTL_SECS
            )
            OneTimeAccess.objects.filter(timestamp__lt=cutoff).delete()

            # try to find matching OTA object
            ota = OneTimeAccess.objects.get(uuid=uuid)

            # get the filename for the SingleAuditReport for this SAC
            use_audit = request.GET.get("beta", "N") == "Y"
            filename = (
                get_filename_from_audit(ota.report_id, "report")
                if use_audit
                else get_filename(ota.report_id, "report")
            )
            download_url = get_download_url(filename)

            # delete the OTA object
            ota.delete()

            # redirect the caller to the file download URL
            return redirect(download_url)

        except OneTimeAccess.DoesNotExist:
            raise Http404()
        except ValidationError:
            raise BadRequest()


class SingleSummaryReportDownloadView(View):
    def get(self, request, report_id):
        """
        Given a report_id in the URL, generate the summary report in S3 and
        redirect to its download link.
        """
        use_audit = request.GET.get("beta", "N") == "Y"
        if use_audit:
            get_object_or_404(Audit, report_id=report_id)
        else:
            get_object_or_404(General, report_id=report_id)

        include_private = include_private_results(request)
        filename, workbook_bytes = (
            generate_summary_report([report_id], include_private)
            if not use_audit
            else generate_audit_summary_report([report_id], include_private)
        )

        # Create an HTTP response with the workbook file for download
        response = HttpResponse(
            workbook_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f"attachment; filename={filename}"

        return response


class MultipleSummaryReportDownloadView(View):
    def post(self, request):
        """
        1. Run a fresh search with the provided search parameters
        2. Get the report_id's from the search
        3. Generate a summary report with the report_ids, which goes into into S3
        4. Redirect to the download url of this new report
        """
        form = AdvancedSearchForm(request.POST)
        use_audit = request.GET.get("beta", "N") == "Y"
        try:
            if form.is_valid():
                form_data = form.cleaned_data
                form_data["advanced_search_flag"] = True
            else:
                raise ValidationError("Form error in Search POST.")

            include_private = include_private_results(request)
            results = run_search(form_data, use_audit)
            results = results[:SUMMARY_REPORT_DOWNLOAD_LIMIT]  # Hard limit XLSX size

            if len(results) == 0:
                raise Http404("Cannot generate summary report. No results found.")
            report_ids = [result.report_id for result in results]
            filename, workbook_bytes = (
                generate_summary_report(report_ids, include_private)
                if not use_audit
                else generate_audit_summary_report(report_ids, include_private)
            )

            # Create an HTTP response with the workbook file for download
            response = HttpResponse(
                workbook_bytes,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = f"attachment; filename={filename}"

            return response

        except Http404 as err:
            logger.info(
                "No results found for MultipleSummaryReportDownloadView post. Suggests an improper or old form submission."
            )
            raise Http404 from err
        except Exception as err:
            logger.info(
                "Unexpected error in MultipleSummaryReportDownloadView post:\n%s", err
            )
            raise BadRequest(err)
