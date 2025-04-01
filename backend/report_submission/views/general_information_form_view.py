import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import render
from django.views import View

from audit.models import (
    Access,
    SingleAuditChecklist,
    LateChangeError,
    SubmissionEvent,
    Audit,
)
from audit.validators import validate_general_information_json

from audit.utils import Util
from config.settings import STATE_ABBREVS

from report_submission.forms import GeneralInformationForm
from report_submission.views.utils import parse_hyphened_date, parse_slashed_date

logger = logging.getLogger(__name__)


class GeneralInformationFormView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            # TODO: Post SOT Launch -> Change this all to use Audit.
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            audit = Audit.objects.find_audit_or_none(report_id=report_id)

            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            sac_context = self._context_from_sac(sac)
            audit_context = self._context_from_audit(audit)
            audit_context = self._dates_to_slashes(audit_context)

            context = self._dates_to_slashes(sac_context)

            self._compare_contexts(context, audit_context)
            return render(request, "report_submission/gen-form.html", context)
        except SingleAuditChecklist.DoesNotExist as err:
            raise PermissionDenied("You do not have access to this audit.") from err

    def post(self, request, *args, **kwargs):
        """
        Handle POST of General Information:
        verify access, validate form data, save, and redirect.
        """
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            form = GeneralInformationForm(request.POST)

            if not form.is_valid():
                context = form.cleaned_data | {
                    "errors": form.errors,
                    "report_id": report_id,
                    "state_abbrevs": STATE_ABBREVS,
                }
                message = ""
                for field, errors in form.errors.items():
                    message = f"{message}\n {field}: {errors}"
                    logger.warning(f"Error {field}: {errors}")
                return render(request, "report_submission/gen-form.html", context)

            form = self._wipe_auditor_address(form)
            form.cleaned_data = self._dates_to_hyphens(form.cleaned_data)
            general_information = sac.general_information
            general_information.update(form.cleaned_data)
            # Remove extra fields based on auditor_country and auditor_international_address and based on audit_period_covered
            # This patch is necessary to filter out unnecessary empty fields returned by the form.
            # We need the call here to account for general information sections created before this code change.
            patched_general_information = Util.remove_extra_fields(general_information)
            validated = validate_general_information_json(
                patched_general_information, False
            )
            sac.general_information = validated
            if general_information.get("audit_type"):
                sac.audit_type = general_information["audit_type"]

            sac.save(
                event_user=request.user,
                event_type=SubmissionEvent.EventType.GENERAL_INFORMATION_UPDATED,
            )

            # Audit Path TODO: Clean-up post POC
            _update_audit(report_id, general_information, request)

            return Util.validate_redirect_url(f"/audit/submission-progress/{report_id}")
        except SingleAuditChecklist.DoesNotExist as err:
            raise PermissionDenied("You do not have access to this audit.") from err
        except ValidationError as err:
            form.cleaned_data = self._dates_to_slashes(form.cleaned_data)
            context = form.cleaned_data | {
                "errors": [err.message],
                "report_id": report_id,
                "state_abbrevs": STATE_ABBREVS,
                "unexpected_errors": True,
            }
            return render(request, "report_submission/gen-form.html", context)
        except LateChangeError:
            return render(request, "audit/no-late-changes.html")
        except Exception as err:
            message = f"Unexpected error in GeneralInformationFormView post. Report ID {report_id}"
            logger.warning(message)
            raise err

    @staticmethod
    def _dates_to_slashes(data):
        """
        Given a general_information object containging both auditee_fiscal_period_start
        and auditee_fiscal_period_start, convert YYYY-MM-DD to MM/DD/YYYY for display.
        """

        data["auditee_fiscal_period_start"] = parse_hyphened_date(
            data.get("auditee_fiscal_period_start", "")
        )
        data["auditee_fiscal_period_end"] = parse_hyphened_date(
            data.get("auditee_fiscal_period_end", "")
        )

        return data

    @staticmethod
    def _dates_to_hyphens(data):
        """
        Given a general_information object containging both auditee_fiscal_period_start
        and auditee_fiscal_period_start, convert MM/DD/YYYY to YYYY-MM-DD for storage.
        """

        data["auditee_fiscal_period_start"] = parse_slashed_date(
            data.get("auditee_fiscal_period_start", "")
        )
        data["auditee_fiscal_period_end"] = parse_slashed_date(
            data.get("auditee_fiscal_period_end", "")
        )

        return data

    @staticmethod
    def _wipe_auditor_address(form):
        """
        Given a general_information form object containing auditor_country, wipe
        unnecessary address data depending on its value.
        """
        # If non-USA is selected, wipe USA-specific fields
        # Else, wipe the non-USA specific field
        keys_to_wipe = [
            "auditor_address_line_1",
            "auditor_city",
            "auditor_state",
            "auditor_zip",
        ]
        if form.cleaned_data.get("auditor_country") == "non-USA":
            for key in keys_to_wipe:
                form.cleaned_data[key] = ""
        else:
            form.cleaned_data["auditor_international_address"] = ""
        return form

    @staticmethod
    def _context_from_audit(audit):
        audit_data = audit.audit if audit and audit.audit else {}
        return (
            {
                "audit_type": audit.audit_type,
                "auditee_fiscal_period_end": audit_data.get(
                    "general_information", {}
                ).get("auditee_fiscal_period_end", ""),
                "auditee_fiscal_period_start": audit_data.get(
                    "general_information", {}
                ).get("auditee_fiscal_period_start", ""),
                "audit_period_covered": audit_data.get("general_information", {}).get(
                    "audit_period_covered"
                ),
                "audit_period_other_months": audit_data.get(
                    "general_information", {}
                ).get("audit_period_other_months", ""),
                "ein": audit_data.get("general_information", {}).get("ein"),
                "ein_not_an_ssn_attestation": audit_data.get(
                    "general_information", {}
                ).get("ein_not_an_ssn_attestation"),
                "multiple_eins_covered": audit_data.get("general_information", {}).get(
                    "multiple_eins_covered"
                ),
                "auditee_uei": audit_data.get("general_information", {}).get(
                    "auditee_uei", ""
                ),
                "multiple_ueis_covered": audit_data.get("general_information", {}).get(
                    "multiple_ueis_covered"
                ),
                "auditee_name": audit_data.get("general_information", {}).get(
                    "auditee_name", ""
                ),
                "auditee_address_line_1": audit_data.get("general_information", {}).get(
                    "auditee_address_line_1", ""
                ),
                "auditee_city": audit_data.get("general_information", {}).get(
                    "auditee_city", ""
                ),
                "auditee_state": audit_data.get("general_information", {}).get(
                    "auditee_state", ""
                ),
                "auditee_zip": audit_data.get("general_information", {}).get(
                    "auditee_zip", ""
                ),
                "auditee_contact_name": audit_data.get("general_information", {}).get(
                    "auditee_contact_name", ""
                ),
                "auditee_contact_title": audit_data.get("general_information", {}).get(
                    "auditee_contact_title", ""
                ),
                "auditee_phone": audit_data.get("general_information", {}).get(
                    "auditee_phone", ""
                ),
                "auditee_email": audit_data.get("general_information", {}).get(
                    "auditee_email", ""
                ),
                "user_provided_organization_type": audit_data.get(
                    "general_information", {}
                ).get("user_provided_organization_type", ""),
                "is_usa_based": audit_data.get("general_information", {}).get(
                    "is_usa_based", ""
                ),
                "auditor_firm_name": audit_data.get("general_information", {}).get(
                    "auditor_firm_name", ""
                ),
                "auditor_ein": audit_data.get("general_information", {}).get(
                    "auditor_ein", ""
                ),
                "auditor_ein_not_an_ssn_attestation": audit_data.get(
                    "general_information", {}
                ).get("auditor_ein_not_an_ssn_attestation", ""),
                "auditor_country": audit_data.get("general_information", {}).get(
                    "auditor_country", ""
                ),
                "auditor_international_address": audit_data.get(
                    "general_information", {}
                ).get("auditor_international_address", ""),
                "auditor_address_line_1": audit_data.get("general_information", {}).get(
                    "auditor_address_line_1", ""
                ),
                "auditor_city": audit_data.get("general_information", {}).get(
                    "auditor_city", ""
                ),
                "auditor_state": audit_data.get("general_information", {}).get(
                    "auditor_state", ""
                ),
                "auditor_zip": audit_data.get("general_information", {}).get(
                    "auditor_zip", ""
                ),
                "auditor_contact_name": audit_data.get("general_information", {}).get(
                    "auditor_contact_name", ""
                ),
                "auditor_contact_title": audit_data.get("general_information", {}).get(
                    "auditor_contact_title", ""
                ),
                "auditor_phone": audit_data.get("general_information", {}).get(
                    "auditor_phone", ""
                ),
                "auditor_email": audit_data.get("general_information", {}).get(
                    "auditor_email", ""
                ),
                "secondary_auditors_exist": audit_data.get(
                    "general_information", {}
                ).get("secondary_auditors_exist", ""),
                "report_id": audit.report_id,
                "state_abbrevs": STATE_ABBREVS,
            }
            if audit
            else {}
        )

    # TODO: Post SOT Launch -> below can be deleted
    @staticmethod
    def _context_from_sac(sac):
        return {
            "audit_type": sac.audit_type,
            "auditee_fiscal_period_end": sac.auditee_fiscal_period_end,
            "auditee_fiscal_period_start": sac.auditee_fiscal_period_start,
            "audit_period_covered": sac.audit_period_covered,
            "audit_period_other_months": sac.audit_period_other_months,
            "ein": sac.ein,
            "ein_not_an_ssn_attestation": sac.ein_not_an_ssn_attestation,
            "multiple_eins_covered": sac.multiple_eins_covered,
            "auditee_uei": sac.auditee_uei,
            "multiple_ueis_covered": sac.multiple_ueis_covered,
            "auditee_name": sac.auditee_name,
            "auditee_address_line_1": sac.auditee_address_line_1,
            "auditee_city": sac.auditee_city,
            "auditee_state": sac.auditee_state,
            "auditee_zip": sac.auditee_zip,
            "auditee_contact_name": sac.auditee_contact_name,
            "auditee_contact_title": sac.auditee_contact_title,
            "auditee_phone": sac.auditee_phone,
            "auditee_email": sac.auditee_email,
            "user_provided_organization_type": sac.user_provided_organization_type,
            "is_usa_based": sac.is_usa_based,
            "auditor_firm_name": sac.auditor_firm_name,
            "auditor_ein": sac.auditor_ein,
            "auditor_ein_not_an_ssn_attestation": sac.auditor_ein_not_an_ssn_attestation,
            "auditor_country": sac.auditor_country,
            "auditor_international_address": sac.auditor_international_address,
            "auditor_address_line_1": sac.auditor_address_line_1,
            "auditor_city": sac.auditor_city,
            "auditor_state": sac.auditor_state,
            "auditor_zip": sac.auditor_zip,
            "auditor_contact_name": sac.auditor_contact_name,
            "auditor_contact_title": sac.auditor_contact_title,
            "auditor_phone": sac.auditor_phone,
            "auditor_email": sac.auditor_email,
            "secondary_auditors_exist": sac.secondary_auditors_exist,
            "report_id": sac.report_id,
            "state_abbrevs": STATE_ABBREVS,
        }

    @staticmethod
    def _compare_contexts(sac_context, audit_context):
        if sac_context != audit_context:
            logger.error(
                f"<SOT ERROR> SAC and Audit Contexts do not match SAC: {sac_context} Audit: {audit_context}"
            )


def _update_audit(report_id, general_information, request):
    audit = Audit.objects.find_audit_or_none(report_id=report_id)
    if audit:
        audit.audit.update({"general_information": general_information})
        audit.save(
            event_user=request.user,
            event_type=SubmissionEvent.EventType.GENERAL_INFORMATION_UPDATED,
        )
