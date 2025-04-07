import logging

from audit.models import Audit
from audit.models.constants import STATUS

from django.http import Http404
from django.shortcuts import render
from django.views.generic import View

from dissemination.views.utils import include_private_results, to_date

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
        audit = Audit.objects.get(report_id=report_id)
        if not audit or audit.submission_status != STATUS.DISSEMINATED:
            raise Http404(f"The report with ID: {report_id} does not exist.")

        include_private = include_private_results(request)
        include_private_and_public = include_private or audit.is_public
        context = {
            "report_id": report_id,
            "header": self._populate_header(audit),
            "auditee_info": self._populate_auditee(audit),
            "auditor_info": self._populate_auditor(audit),
            "summary": self._populate_summary(audit, include_private_and_public),
            "allow_download": include_private_and_public,
        }
        return render(request, "audit_summary.html", context)

    @staticmethod
    def _populate_header(audit):
        return {
            "auditee_name": audit.auditee_name,
            "auditee_uei": audit.auditee_uei,
            "fac_accepted_date": to_date(audit.fac_accepted_date),
            "report_id": audit.report_id,
            "fy_start_date": to_date(
                audit.audit["general_information"]["auditee_fiscal_period_start"]
            ),
            "fy_end_date": to_date(
                audit.audit["general_information"]["auditee_fiscal_period_end"]
            ),
        }

    @staticmethod
    def _populate_auditee(audit):
        auditee_signature = audit.audit["auditee_certification"]["auditee_signature"]
        auditee_general_keys = {
            "auditee_contact_name",
            "auditee_contact_title",
            "auditee_email",
            "auditee_phone",
            "auditee_address_line_1",
            "auditee_city",
            "auditee_state",
            "auditee_zip",
            "ein",
        }
        auditee_info = {
            key: audit.audit["general_information"].get(key, "")
            for key in auditee_general_keys
        }

        return {
            "additional_eins": "Y" if audit.audit.get("additional_eins", []) else "N",
            "additional_ueis": "Y" if audit.audit.get("additional_ueis", []) else "N",
            "auditee_certify_name": auditee_signature["auditee_name"],
            "auditee_certify_title": auditee_signature["auditee_title"],
            **auditee_info,
        }

    @staticmethod
    def _populate_auditor(audit):
        auditor_general_keys = {
            "auditor_contact_name",
            "auditor_contact_title",
            "auditor_email",
            "auditor_phone",
            "auditor_address_line_1",
            "auditor_city",
            "auditor_state",
            "auditor_zip",
            "auditor_foreign_address",
        }
        # secondary auditors
        auditor_info = {
            key: audit.audit["general_information"].get(key, "")
            for key in auditor_general_keys
        }
        return {
            "has_secondary_auditors": (
                "Y"
                if audit.audit["general_information"].get(
                    "secondary_auditors_exist", False
                )
                else "N"
            ),
            **auditor_info,
        }

    @staticmethod
    def _populate_summary(audit, is_public):
        notes_count = 0

        # The main notes_to_sefa object counts as 1 note unless there are entries.
        if audit.audit["notes_to_sefa"]:
            num_notes_entries = len(
                audit.audit["notes_to_sefa"].get("notes_to_sefa_entries", [])
            )
            notes_count = max(1, num_notes_entries)

        return {
            "number_of_federal_awards": len(
                audit.audit["federal_awards"].get("awards", [])
            ),
            "number_of_notes": notes_count if is_public else "N/A",
            "number_of_findings": audit.audit.get("search_indexes", {}).get(
                "unique_audit_findings_count", 0
            ),
            "number_of_findings_text": (
                len(audit.audit.get("findings_text", [])) if is_public else "N/A"
            ),
            "number_of_caps": (
                len(audit.audit.get("corrective_action_plan", []))
                if is_public
                else "N/A"
            ),
            "total_amount_expended": audit.audit["federal_awards"][
                "total_amount_expended"
            ],
        }
