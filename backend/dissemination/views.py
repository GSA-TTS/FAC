import math

from django.core.exceptions import BadRequest, PermissionDenied
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import View

from audit.file_downloads import get_download_url, get_filename
from audit.models import SingleAuditChecklist

from dissemination.forms import SearchForm
from dissemination.search import search_general
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
)

from users.permissions import can_read_tribal

def include_private_results(request):
    if not request.user.is_authenticated:
        return False
    
    if not can_read_tribal(request.user):
        return False
    
    return True


class Search(View):
    def get(self, request, *args, **kwargs):
        form = SearchForm()

        return render(request, "search.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = SearchForm(request.POST)
        results = []
        context = {}

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

            # TODO: Add a limit choice field to the form
            limit = form.cleaned_data["limit"] or 30
            # Changed in the form via pagination links
            page = int(form.cleaned_data["page"] or 1)

            # is the user authenticated?
            include_private = include_private_results(request)

            print(include_private)

            results = search_general(
                names=names,
                alns=alns,
                uei_or_eins=uei_or_eins,
                start_date=start_date,
                end_date=end_date,
                cog_or_oversight=cog_or_oversight,
                agency_name=agency_name,
                audit_years=audit_years,
                include_private=include_private,
            )
            results_count = results.count()
            # Reset page to one if the page number surpasses how many pages there actually are
            if page > math.ceil(results_count / limit):
                page = 1

            paginator = Paginator(object_list=results, per_page=limit)
            results = paginator.get_page(page)  # List of size <limit> objects
            results.adjusted_elided_pages = paginator.get_elided_page_range(
                page, on_each_side=1
            )  # Pagination buttons, adjust ellipses around the current page

            # Reformat these so the date-picker elements in HTML prepopulate
            if form.cleaned_data["start_date"]:
                form.cleaned_data["start_date"] = start_date.strftime("%Y-%m-%d")
            if form.cleaned_data["end_date"]:
                form.cleaned_data["end_date"] = end_date.strftime("%Y-%m-%d")
        else:
            raise BadRequest("Form data validation error.", form.errors)

        context = context | {
            "form": form,
            "limit": limit,
            "results": results,
            "results_count": results_count,
            "page": page,
        }

        return render(request, "search.html", context)


class AuditSummaryView(View):
    def get(self, request, report_id):
        """
        Grab any information about the given report in the dissemination tables.
        1.  See if this audit is available in the dissemination tables. If not, 404.
        2.  Grab all relevant info from dissem tables. Some items may not exist if they had no findings.
        3.  Wrap up the data all nice in a context object for display.
        """

        # Viewable audits __MUST__ be public.
        general = General.objects.filter(report_id=report_id, is_public=True)
        if not general.exists():
            raise Http404(
                "The report with this ID does not exist in the dissemination database."
            )
        general_data = general.values()[0]
        del general_data["id"]

        data = self.get_audit_content(report_id)

        # Add entity name and UEI to the context, for the footer bit.
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
        We may want to define additional functions to squish this information down
        further. I.e. remove DB ids or something.
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

        data["Awards"] = [
            x for x in awards.values()
        ]  # Take QuerySet to a list of objects

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


class PdfDownloadView(View):
    def get(self, request, report_id):
        # only allow PDF downloads for disseminated submissions
        disseminated = get_object_or_404(General, report_id=report_id)

        # only allow PDF downloads for public submissions
        if not disseminated.is_public:
            raise PermissionDenied("You do not have access to this audit report.")

        sac = get_object_or_404(SingleAuditChecklist, report_id=report_id)
        filename = get_filename(sac, "report")

        return redirect(get_download_url(filename))


class XlsxDownloadView(View):
    def get(self, request, report_id, file_type):
        # only allow xlsx downloads from disseminated submissions
        disseminated = get_object_or_404(General, report_id=report_id)

        # only allow xlsx downloads for public submissions
        if not disseminated.is_public:
            raise PermissionDenied("You do not have access to this file.")

        sac = get_object_or_404(SingleAuditChecklist, report_id=report_id)
        filename = get_filename(sac, file_type)

        return redirect(get_download_url(filename))
