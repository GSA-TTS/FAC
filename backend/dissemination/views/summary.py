import logging
from dissemination.models import (
    AdditionalEin,
    AdditionalUei,
    CapText,
    DisseminationCombined,
    FederalAward,
    Finding,
    FindingText,
    General,
    Note,
    SecondaryAuditor,
)

from django.http import Http404
from django.shortcuts import render
from django.views.generic import View

from dissemination.views.utils import include_private_results

logger = logging.getLogger(__name__)


class AuditSummaryView(View):
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

        include_private = include_private_results(request)
        include_private_and_public = include_private or general_data["is_public"]
        data = self.get_audit_content(report_id, include_private_and_public)
        is_sf_sac_downloadable = DisseminationCombined.objects.filter(
            report_id=report_id
        ).exists()

        # Add entity name and UEI to the context, for the footer.
        context = {
            "report_id": report_id,
            "auditee_name": general_data["auditee_name"],
            "auditee_uei": general_data["auditee_uei"],
            "general": general_data,
            "include_private": include_private,
            "data": data,
            "is_sf_sac_downloadable": is_sf_sac_downloadable,
        }

        return render(request, "summary.html", context)

    def get_audit_content(self, report_id, include_private_and_public):
        """
        Grab everything relevant from the dissemination tables.
        Wrap that data into a dict, and return it.
        """
        awards = FederalAward.objects.filter(report_id=report_id)
        audit_findings = (
            Finding.objects.filter(report_id=report_id)
            .order_by("reference_number")
            .distinct("reference_number")
        )
        audit_findings_text = FindingText.objects.filter(report_id=report_id)
        corrective_action_plan = CapText.objects.filter(report_id=report_id)
        notes_to_sefa = Note.objects.filter(report_id=report_id)
        secondary_auditors = SecondaryAuditor.objects.filter(report_id=report_id)
        additional_ueis = AdditionalUei.objects.filter(report_id=report_id)
        additional_eins = AdditionalEin.objects.filter(report_id=report_id)

        data = {"Awards": [x for x in awards.values()]}

        # QuerySet values to an array of dicts
        if notes_to_sefa.exists() and include_private_and_public:
            data["Notes to SEFA"] = [x for x in notes_to_sefa.values()]
        if audit_findings.exists():
            data["Audit Findings"] = [x for x in audit_findings.values()]
        if audit_findings_text.exists() and include_private_and_public:
            data["Audit Findings Text"] = [x for x in audit_findings_text.values()]
        if corrective_action_plan.exists() and include_private_and_public:
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
