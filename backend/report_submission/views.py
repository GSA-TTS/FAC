import logging
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import BadRequest, PermissionDenied, ValidationError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

import api.views

from audit.cross_validation import sac_validation_shape
from audit.cross_validation.naming import NC, SECTION_NAMES as SN
from audit.cross_validation.submission_progress_check import section_completed_metadata

from audit.models import Access, SingleAuditChecklist, LateChangeError, SubmissionEvent
from audit.validators import validate_general_information_json

from config.settings import STATIC_SITE_URL, STATE_ABBREVS

from report_submission.forms import AuditeeInfoForm, GeneralInformationForm

logger = logging.getLogger(__name__)


class ReportSubmissionRedirectView(View):
    def get(self, request):
        return redirect(reverse("report_submission:eligibility"))


# Step 1
class EligibilityFormView(LoginRequiredMixin, View):
    def get(self, request):
        args = {}
        args["step"] = 1
        return render(request, "report_submission/step-1.html", args)

    # render eligibility form

    # gather/save step 1 info, redirect to step 2
    def post(self, post_request):
        eligibility = api.views.eligibility_check(post_request.user, post_request.POST)
        if eligibility.get("eligible"):
            return redirect(reverse("report_submission:auditeeinfo"))

        return redirect(reverse("report_submission:eligibility"))


# Step 2
class AuditeeInfoFormView(LoginRequiredMixin, View):
    def get(self, request):
        args = {}
        args["step"] = 2
        args["form"] = AuditeeInfoForm()
        return render(request, "report_submission/step-2.html", args)

    # render auditee info form

    # gather/save step 2 info, redirect to step 3
    def post(self, request):
        form = AuditeeInfoForm(request.POST)
        if not form.is_valid():
            context = {
                "form": form,
                "step": 2,
            }
            return render(request, "report_submission/step-2.html", context)

        formatted_post = {
            "csrfmiddlewaretoken": request.POST.get("csrfmiddlewaretoken"),
            "auditee_uei": form.cleaned_data["auditee_uei"].upper(),
            "auditee_address_line_1": request.POST.get("auditee_address_line_1"),
            "auditee_city": request.POST.get("auditee_city"),
            "auditee_state": request.POST.get("auditee_state"),
            "auditee_zip": request.POST.get("auditee_zip"),
            "auditee_fiscal_period_start": form.cleaned_data[
                "auditee_fiscal_period_start"
            ].strftime("%Y-%m-%d"),
            "auditee_fiscal_period_end": form.cleaned_data[
                "auditee_fiscal_period_end"
            ].strftime("%Y-%m-%d"),
        }

        info_check = api.views.auditee_info_check(request.user, formatted_post)
        if info_check.get("errors"):
            return redirect(reverse("report_submission:auditeeinfo"))

        return redirect(reverse("report_submission:accessandsubmission"))


# Step 3
class AccessAndSubmissionFormView(LoginRequiredMixin, View):
    def get(self, request):
        args = {}
        args["step"] = 3
        return render(request, "report_submission/step-3.html", args)

    # render access-submission form

    # gather/save step 3 info, redirect to step ...4?
    def post(self, post_request):
        result = api.views.access_and_submission_check(
            post_request.user, post_request.POST
        )

        report_id = result.get("report_id")

        if report_id:
            return redirect(f"/report_submission/general-information/{report_id}")
        else:
            return redirect(reverse("report_submission:accessandsubmission"))


class GeneralInformationFormView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            # this should probably be a permission mixin
            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            context = {
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
                "report_id": report_id,
                "state_abbrevs": STATE_ABBREVS,
            }

            context = self._dates_to_slashes(context)

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
            validated = validate_general_information_json(general_information)
            sac.general_information = validated
            if general_information.get("audit_type"):
                sac.audit_type = general_information["audit_type"]

            sac.save(
                event_user=request.user,
                event_type=SubmissionEvent.EventType.GENERAL_INFORMATION_UPDATED,
            )

            return redirect(f"/audit/submission-progress/{report_id}")
        except SingleAuditChecklist.DoesNotExist as err:
            raise PermissionDenied("You do not have access to this audit.") from err
        except ValidationError as err:
            message = f"ValidationError for report ID {report_id}: {err.message}"
            raise BadRequest(message)
        except LateChangeError:
            return render(request, "audit/no-late-changes.html")
        except Exception as err:
            message = f"Unexpected error in GeneralInformationFormView post. Report ID {report_id}"
            logger.warning(message)
            raise err

    def _dates_to_slashes(self, data):
        """
        Given a general_information object containging both auditee_fiscal_period_start
        and auditee_fiscal_period_start, convert YYYY-MM-DD to MM/DD/YYYY for display.
        """
        try:
            datetime_object_start = datetime.strptime(
                data.get("auditee_fiscal_period_start", ""), "%Y-%m-%d"
            )
            datetime_object_end = datetime.strptime(
                data.get("auditee_fiscal_period_end", ""), "%Y-%m-%d"
            )
            data["auditee_fiscal_period_start"] = datetime_object_start.strftime(
                "%m/%d/%Y"
            )
            data["auditee_fiscal_period_end"] = datetime_object_end.strftime("%m/%d/%Y")
        except Exception:
            return data
        return data

    def _dates_to_hyphens(self, data):
        """
        Given a general_information object containging both auditee_fiscal_period_start
        and auditee_fiscal_period_start, convert MM/DD/YYYY to YYYY-MM-DD for storage.
        """
        try:
            datetime_object_start = datetime.strptime(
                data.get("auditee_fiscal_period_start", ""), "%m/%d/%Y"
            )
            datetime_object_end = datetime.strptime(
                data.get("auditee_fiscal_period_end", ""), "%m/%d/%Y"
            )
            data["auditee_fiscal_period_start"] = datetime_object_start.strftime(
                "%Y-%m-%d"
            )
            data["auditee_fiscal_period_end"] = datetime_object_end.strftime("%Y-%m-%d")
        except Exception:
            return data
        return data

    def _wipe_auditor_address(self, form):
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


class UploadPageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        instructions_base_url = STATIC_SITE_URL + "resources/workbooks/"
        workbook_base_url = STATIC_SITE_URL + "assets/workbooks/"

        # Organized by URL name, page specific constants are defined here
        # Data can then be accessed by checking the current URL
        additional_context = {
            "federal-awards": {
                "view_id": "federal-awards",
                "view_name": "Federal awards",
                "instructions": "Enter the federal awards you received in the last audit year using the provided worksheet.",
                "DB_id": SN[NC.FEDERAL_AWARDS].snake_case,
                "instructions_url": instructions_base_url + "federal-awards/",
                "workbook_url": workbook_base_url + "federal-awards-workbook.xlsx",
                # below URL handled as a special case because of inconsistent name usage in audit/urls.py and audit/cross_validation/naming.py
                "existing_workbook_url": reverse(
                    "audit:FederalAwardsExpended", args=[report_id]
                ),
            },
            "notes-to-sefa": {
                "view_id": "notes-to-sefa",
                "view_name": "Notes to SEFA",
                "instructions": "Enter the notes on the Schedule of Expenditures of Federal Awards (SEFA) using the provided worksheet.",
                "DB_id": SN[NC.NOTES_TO_SEFA].snake_case,
                "instructions_url": instructions_base_url + "notes-to-sefa/",
                "workbook_url": workbook_base_url + "notes-to-sefa-workbook.xlsx",
                "existing_workbook_url": reverse(
                    f"audit:{SN[NC.NOTES_TO_SEFA].camel_case}", args=[report_id]
                ),
            },
            "audit-findings": {
                "view_id": "audit-findings",
                "view_name": "Audit findings",
                "instructions": "Enter the audit findings for your federal awards using the provided worksheet.",
                "DB_id": SN[NC.FINDINGS_UNIFORM_GUIDANCE].snake_case,
                "instructions_url": instructions_base_url
                + "federal-awards-audit-findings/",
                "no_findings_disclaimer": True,
                "workbook_url": workbook_base_url
                + "federal-awards-audit-findings-workbook.xlsx",
                "existing_workbook_url": reverse(
                    f"audit:{SN[NC.FINDINGS_UNIFORM_GUIDANCE].camel_case}",
                    args=[report_id],
                ),
            },
            "audit-findings-text": {
                "view_id": "audit-findings-text",
                "view_name": "Audit findings text",
                "instructions": "Enter the text for your audit findings using the provided worksheet.",
                "DB_id": SN[NC.FINDINGS_TEXT].snake_case,
                "instructions_url": instructions_base_url
                + "federal-awards-audit-findings-text/",
                "no_findings_disclaimer": True,
                "workbook_url": workbook_base_url + "audit-findings-text-workbook.xlsx",
                "existing_workbook_url": reverse(
                    f"audit:{SN[NC.FINDINGS_TEXT].camel_case}", args=[report_id]
                ),
            },
            "cap": {
                "view_id": "cap",
                "view_name": "Corrective Action Plan (CAP)",
                "instructions": "Enter your CAP text using the provided worksheet.",
                "DB_id": SN[NC.CORRECTIVE_ACTION_PLAN].snake_case,
                "instructions_url": instructions_base_url + "corrective-action-plan/",
                "no_findings_disclaimer": True,
                "workbook_url": workbook_base_url
                + "corrective-action-plan-workbook.xlsx",
                "existing_workbook_url": reverse(
                    f"audit:{SN[NC.CORRECTIVE_ACTION_PLAN].camel_case}",
                    args=[report_id],
                ),
            },
            "additional-ueis": {
                "view_id": "additional-ueis",
                "view_name": "Additional UEIs",
                "instructions": "Enter any additional UEIs using the provided worksheet.",
                "DB_id": SN[NC.ADDITIONAL_UEIS].snake_case,
                "instructions_url": instructions_base_url + "additional-ueis-workbook/",
                "workbook_url": workbook_base_url + "additional-ueis-workbook.xlsx",
                "existing_workbook_url": reverse(
                    "audit:AdditionalUeis", args=[report_id]
                ),
            },
            "secondary-auditors": {
                "view_id": "secondary-auditors",
                "view_name": "Secondary auditors",
                "instructions": "Enter any additional auditors using the provided worksheet.",
                "DB_id": SN[NC.SECONDARY_AUDITORS].snake_case,
                "instructions_url": instructions_base_url
                + "secondary-auditors-workbook/",
                "workbook_url": workbook_base_url + "secondary-auditors-workbook.xlsx",
                # below URL handled as a special case because of inconsistent name usage in audit/urls.py and audit/cross_validation/naming.py
                "existing_workbook_url": reverse(
                    f"audit:{SN[NC.SECONDARY_AUDITORS].camel_case}", args=[report_id]
                ),
            },
            "additional-eins": {
                "view_id": "additional-eins",
                "view_name": "Additional EINs",
                "instructions": "Enter any additional EINs using the provided worksheet.",
                "DB_id": SN[NC.ADDITIONAL_EINS].snake_case,
                "instructions_url": instructions_base_url + "additional-eins-workbook/",
                "workbook_url": workbook_base_url + "additional-eins-workbook.xlsx",
                # below URL handled as a special case because of inconsistent name usage in audit/urls.py and audit/cross_validation/naming.py
                "existing_workbook_url": reverse(
                    "audit:AdditionalEins", args=[report_id]
                ),
            },
        }

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            # Context for every upload page
            context = {
                "auditee_name": sac.auditee_name,
                "report_id": report_id,
                "auditee_uei": sac.auditee_uei,
                "user_provided_organization_type": sac.user_provided_organization_type,
            }
            # Using the current URL, append page specific context
            path_name = request.path.split("/")[2]

            for item in additional_context[path_name]:
                context[item] = additional_context[path_name][item]
            try:
                context["already_submitted"] = getattr(
                    sac, additional_context[path_name]["DB_id"]
                )

                shaped_sac = sac_validation_shape(sac)
                completed_metadata = section_completed_metadata(shaped_sac, path_name)

                context["last_uploaded_by"] = completed_metadata[0]
                context["last_uploaded_at"] = completed_metadata[1]

            except Exception:
                context["already_submitted"] = None

            return render(request, "report_submission/upload-page.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            return redirect(
                "/audit/submission-progress/{report_id}".format(report_id=report_id)
            )

        except Exception as e:
            logger.info("Unexpected error in UploadPageView post.\n", e)

        raise BadRequest()
