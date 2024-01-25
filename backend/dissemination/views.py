from collections import namedtuple
from datetime import timedelta
import logging
import math

from django.conf import settings
from django.core.exceptions import BadRequest, ValidationError
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import View

from audit.models import SingleAuditChecklist

from config.settings import STATE_ABBREVS, SUMMARY_REPORT_DOWNLOAD_LIMIT

from dissemination.file_downloads import get_download_url, get_filename
from dissemination.forms import SearchForm
from dissemination.search import search_general
from dissemination.mixins import ReportAccessRequiredMixin
from dissemination.models import (
    General,
    FederalAward,
    Finding,
    FindingText,
    CapText,
    Note,
    SecondaryAuditor,
    AdditionalEin,
    AdditionalUei,
    OneTimeAccess,
)
from dissemination.summary_reports import generate_summary_report

from users.permissions import can_read_tribal

logger = logging.getLogger(__name__)


def include_private_results(request):
    """
    Determine if the user is authenicated to see private data.
    """
    if not request.user.is_authenticated:
        return False

    if not can_read_tribal(request.user):
        return False

    return True


def clean_form_data(form):
    """
    Given a SearchForm, return a namedtuple with its cleaned and formatted data.
    Ideally, this makes accessing form data later a little more readable.
    """
    FormData = namedtuple(
        "FormData",
        "uei_or_eins alns names start_date end_date cog_or_oversight agency_name audit_years auditee_state order_by order_direction limit page",
    )

    if form.is_valid():
        uei_or_eins = form.cleaned_data["uei_or_ein"].splitlines()
        alns = form.cleaned_data["aln"].replace(", ", " ").split()
        names = form.cleaned_data["entity_name"].splitlines()
        start_date = form.cleaned_data["start_date"]
        end_date = form.cleaned_data["end_date"]
        cog_or_oversight = form.cleaned_data["cog_or_oversight"]
        agency_name = form.cleaned_data["agency_name"]
        audit_years = [
            int(year) for year in form.cleaned_data["audit_year"]
        ]  # Cast strings from HTML to int
        auditee_state = form.cleaned_data["auditee_state"]
        order_by = form.cleaned_data["order_by"]
        order_direction = form.cleaned_data["order_direction"]

        # TODO: Add a limit choice field to the form
        limit = form.cleaned_data["limit"] or 30
        page = int(form.cleaned_data["page"] or 1)

        form_data = FormData(
            uei_or_eins,
            alns,
            names,
            start_date,
            end_date,
            cog_or_oversight,
            agency_name,
            audit_years,
            auditee_state,
            order_by,
            order_direction,
            limit,
            page,
        )

    else:
        raise BadRequest("Form data validation error.", form.errors)

    return form_data


def run_search_general(form_data, include_private):
    """
    Given cleaned form data and an 'include_private' boolean, run the search.
    Returns the results QuerySet.
    """
    return search_general(
        names=form_data.names,
        alns=form_data.alns,
        uei_or_eins=form_data.uei_or_eins,
        start_date=form_data.start_date,
        end_date=form_data.end_date,
        cog_or_oversight=form_data.cog_or_oversight,
        agency_name=form_data.agency_name,
        audit_years=form_data.audit_years,
        auditee_state=form_data.auditee_state,
        include_private=include_private,
        order_by=form_data.order_by,
        order_direction=form_data.order_direction,
    )


class Search(View):
    def get(self, request, *args, **kwargs):
        """
        When accessing the search page through get, return the blank search page.
        """
        form = SearchForm()

        return render(
            request,
            "search.html",
            {
                "form": form,
                "state_abbrevs": STATE_ABBREVS,
                "summary_report_download_limit": SUMMARY_REPORT_DOWNLOAD_LIMIT,
            },
        )

    def post(self, request, *args, **kwargs):
        """
        When accessing the search page through post, run a search and display the results.
        """
        form = SearchForm(request.POST)
        results = []
        context = {}

        form_data = clean_form_data(form)
        include_private = include_private_results(request)
        results = run_search_general(form_data, include_private)

        results_count = len(results)
        # Reset page to one if the page number surpasses how many pages there actually are
        page = form_data.page
        if page > math.ceil(results_count / form_data.limit):
            page = 1

        # The paginator object handles splicing the results to a one-page iterable and calculates which page numbers to show.
        paginator = Paginator(object_list=results, per_page=form_data.limit)
        results = paginator.get_page(form_data.page)
        results.adjusted_elided_pages = paginator.get_elided_page_range(
            form_data.page, on_each_side=1
        )

        # Reformat these so the date-picker elements in HTML prepopulate
        if form.cleaned_data["start_date"]:
            form.cleaned_data["start_date"] = form.cleaned_data["start_date"].strftime(
                "%Y-%m-%d"
            )
        if form.cleaned_data["end_date"]:
            form.cleaned_data["end_date"] = form.cleaned_data["end_date"].strftime(
                "%Y-%m-%d"
            )

        context = context | {
            "form": form,
            "state_abbrevs": STATE_ABBREVS,
            "limit": form_data.limit,
            "results": results,
            "results_count": results_count,
            "page": page,
            "order_by": form_data.order_by,
            "order_direction": form_data.order_direction,
            "summary_report_download_limit": SUMMARY_REPORT_DOWNLOAD_LIMIT,
        }

        return render(request, "search.html", context)


class AuditSummaryView(ReportAccessRequiredMixin, View):
    def get(self, request, report_id):
        """
        Display information about the given report in the dissemination tables.
        1.  See if this audit is available. If not, 404.
        2.  Grab all relevant info from the dissemination tables.
        3.  Wrap the data into a context object for display.
        """
        # Viewable audits __MUST__ be public.
        general = General.objects.filter(report_id=report_id)
        if not general.exists():
            raise Http404(
                "The report with this ID does not exist in the dissemination database."
            )
        general_data = general.values()[0]
        del general_data["id"]

        data = self.get_audit_content(report_id)

        # Add entity name and UEI to the context, for the footer.
        context = {
            "report_id": report_id,
            "auditee_name": general_data["auditee_name"],
            "auditee_uei": general_data["auditee_uei"],
            "general": general_data,
            "data": data,
        }

        return render(request, "summary.html", context)

    def get_audit_content(self, report_id):
        """
        Grab everything relevant from the dissemination tables.
        Wrap that data into a dict, and return it.
        """
        awards = FederalAward.objects.filter(report_id=report_id)
        audit_findings = Finding.objects.filter(report_id=report_id)
        audit_findings_text = FindingText.objects.filter(report_id=report_id)
        corrective_action_plan = CapText.objects.filter(report_id=report_id)
        notes_to_sefa = Note.objects.filter(report_id=report_id)
        secondary_auditors = SecondaryAuditor.objects.filter(report_id=report_id)
        additional_ueis = AdditionalUei.objects.filter(report_id=report_id)
        additional_eins = AdditionalEin.objects.filter(report_id=report_id)

        data = {}

        # QuerySet values to an array of dicts
        data["Awards"] = [x for x in awards.values()]
        if notes_to_sefa.exists():
            data["Notes to SEFA"] = [x for x in notes_to_sefa.values()]
        if audit_findings.exists():
            data["Audit Findings"] = [x for x in audit_findings.values()]
        if audit_findings_text.exists():
            data["Audit Findings Text"] = [x for x in audit_findings_text.values()]
        if corrective_action_plan.exists():
            data["Corrective Action Plan"] = [
                x for x in corrective_action_plan.values()
            ]
        if secondary_auditors.exists():
            data["Secondary Auditors"] = [x for x in secondary_auditors.values()]
        if additional_ueis.exists():
            data["Additional UEIs"] = [x for x in additional_ueis.values()]
        if additional_eins.exists():
            data["Additional EINs"] = [x for x in additional_eins.values()]

        return data


class PdfDownloadView(ReportAccessRequiredMixin, View):
    def get(self, request, report_id):
        """
        Given a report_id in the URL, find the relevant PDF in S3 and
        redirect to the download link.
        """
        # only allow PDF downloads for disseminated submissions
        get_object_or_404(General, report_id=report_id)

        sac = get_object_or_404(SingleAuditChecklist, report_id=report_id)
        filename = get_filename(sac, "report")

        return redirect(get_download_url(filename))


class XlsxDownloadView(ReportAccessRequiredMixin, View):
    def get(self, request, report_id, file_type):
        """
        Given a report_id and workbook section (file_type) in the URL,
        find the relevant XLSX file in S3 and redirect to its download link.
        """
        # only allow xlsx downloads from disseminated submissions
        get_object_or_404(General, report_id=report_id)

        sac = get_object_or_404(SingleAuditChecklist, report_id=report_id)
        filename = get_filename(sac, file_type)

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

            # try to find the SingleAuditChecklist associated with this OTA
            sac = get_object_or_404(SingleAuditChecklist, report_id=ota.report_id)

            # get the filename for the SingleAuditReport for this SAC
            filename = get_filename(sac, "report")
            download_url = get_download_url(filename)

            # delete the OTA object
            ota.delete()

            # redirect the caller to the file download URL
            return redirect(download_url)

        except OneTimeAccess.DoesNotExist:
            raise Http404()
        except ValidationError:
            raise BadRequest()


class SingleSummaryReportDownloadView(ReportAccessRequiredMixin, View):
    def get(self, request, report_id):
        """
        Given a report_id in the URL, generate the summary report in S3 and
        redirect to its download link.
        """
        sac = get_object_or_404(General, report_id=report_id)
        filename = generate_summary_report([sac.report_id])
        download_url = get_download_url(filename)

        return redirect(download_url)


class MultipleSummaryReportDownloadView(View):
    def post(self, request):
        """
        1. Run a fresh search with the provided search parameters
        2. Get the report_id's from the search
        3. Generate a summary report with the report_ids, which goes into into S3
        4. Redirect to the download url of this new report
        """
        form = SearchForm(request.POST)

        try:
            cleaned_data = clean_form_data(form)
            include_private = include_private_results(request)
            results = run_search_general(cleaned_data, include_private)
            results = results[:SUMMARY_REPORT_DOWNLOAD_LIMIT]  # Hard limit XLSX size

            if len(results) == 0:
                raise Http404("Cannot generate summary report. No results found.")
            report_ids = [result.report_id for result in results]

            filename = generate_summary_report(report_ids)
            download_url = get_download_url(filename)

            return redirect(download_url)

        except Http404 as err:
            logger.info(
                "No results found for MultipleSummaryReportDownloadView post. Suggests an improper or old form submission."
            )
            raise Http404 from err
        except Exception as err:
            logger.info(
                "Enexpected error in MultipleSummaryReportDownloadView post:\n%s", err
            )
            raise BadRequest(err)
