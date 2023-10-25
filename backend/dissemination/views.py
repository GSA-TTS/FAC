from django.core.exceptions import PermissionDenied
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
    Passthrough,
    Finding,
    FindingText,
    CapText,
    Note,
)


class Search(View):
    def get(self, request, *args, **kwargs):
        form = SearchForm()

        return render(request, "search.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = SearchForm(request.POST)
        results = []

        if form.is_valid():
            names = form.cleaned_data["entity_name"].splitlines()
            uei_or_eins = form.cleaned_data["uei_or_ein"].splitlines()
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]
            cog_or_oversight = form.cleaned_data["cog_or_oversight"]
            agency_name = form.cleaned_data["agency_name"]
            audit_years = [
                int(year) for year in form.cleaned_data["audit_year"]
            ]  # Cast strings from HTML to int

            results = search_general(
                names,
                uei_or_eins,
                start_date,
                end_date,
                cog_or_oversight,
                agency_name,
                audit_years,
            )
            # Reformat these so the date-picker elements in HTML prepopulate
            if form.cleaned_data["start_date"]:
                form.cleaned_data["start_date"] = start_date.strftime("%Y-%m-%d")
            if form.cleaned_data["end_date"]:
                form.cleaned_data["end_date"] = end_date.strftime("%Y-%m-%d")

        return render(request, "search.html", {"form": form, "results": results})


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
        passthrough_entities = Passthrough.objects.filter(report_id=report_id)
        audit_findings = Finding.objects.filter(report_id=report_id)
        audit_findings_text = FindingText.objects.filter(report_id=report_id)
        corrective_action_plan = CapText.objects.filter(report_id=report_id)
        notes_to_sefa = Note.objects.filter(report_id=report_id)

        data = {}

        data["Awards"] = [
            x for x in awards.values()
        ]  # Take QuerySet to a list of objects

        if passthrough_entities.exists():
            data["Passthrough Entities"] = [x for x in passthrough_entities.values()]
        if audit_findings.exists():
            data["Audit Findings"] = [x for x in audit_findings.values()]
        if audit_findings_text.exists():
            data["Audit Findings Text"] = [x for x in audit_findings_text.values()]
        if corrective_action_plan.exists():
            data["Corrective Action Plan"] = [
                x for x in corrective_action_plan.values()
            ]
        if notes_to_sefa.exists():
            data["Notes"] = [x for x in notes_to_sefa.values()]

        for key in data:
            for item in data[key]:
                del item["id"]
                del item["report_id"]

        return data


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
