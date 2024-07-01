import logging
from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import BadRequest, PermissionDenied, ValidationError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib import messages

import api.views

from audit.cross_validation import sac_validation_shape
from audit.cross_validation.naming import NC, SECTION_NAMES as SN
from audit.cross_validation.submission_progress_check import section_completed_metadata

from audit.models import Access, SingleAuditChecklist, LateChangeError, SubmissionEvent
from audit.validators import validate_general_information_json

from audit.utils import Util
from audit.models.models import ExcelFile
from audit.fixtures.excel import FORM_SECTIONS
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
        entry_form_data = request.user.profile.entry_form_data
        eligible = api.views.eligibility_check(request.user, entry_form_data)

        # Prevent users from skipping the eligibility form
        if not eligible.get("eligible"):
            return redirect(reverse("report_submission:eligibility"))
        else:
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
        info_check = api.views.auditee_info_check(
            request.user, request.user.profile.entry_form_data
        )

        # Prevent users from skipping the auditee info form
        if info_check.get("errors"):
            return redirect(reverse("report_submission:auditeeinfo"))
        else:
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

            return redirect(f"/audit/submission-progress/{report_id}")
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

    def _dates_to_slashes(self, data):
        """
        Given a general_information object containging both auditee_fiscal_period_start
        and auditee_fiscal_period_start, convert YYYY-MM-DD to MM/DD/YYYY for display.
        """

        data["auditee_fiscal_period_start"] = self._parse_hyphened_date(
            data.get("auditee_fiscal_period_start", "")
        )
        data["auditee_fiscal_period_end"] = self._parse_hyphened_date(
            data.get("auditee_fiscal_period_end", "")
        )

        return data

    def _parse_slashed_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            return date_str

    def _parse_hyphened_date(self, date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%m/%d/%Y")
        except ValueError:
            return date_str

    def _dates_to_hyphens(self, data):
        """
        Given a general_information object containging both auditee_fiscal_period_start
        and auditee_fiscal_period_start, convert MM/DD/YYYY to YYYY-MM-DD for storage.
        """

        data["auditee_fiscal_period_start"] = self._parse_slashed_date(
            data.get("auditee_fiscal_period_start", "")
        )
        data["auditee_fiscal_period_end"] = self._parse_slashed_date(
            data.get("auditee_fiscal_period_end", "")
        )

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
                "remove_existing_workbook": reverse(
                    f"report_submission:delete-{SN[NC.FINDINGS_UNIFORM_GUIDANCE].url_tail}",
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
                "remove_existing_workbook": reverse(
                    f"report_submission:delete-{SN[NC.FINDINGS_TEXT].url_tail}",
                    args=[report_id],
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
                "remove_existing_workbook": reverse(
                    f"report_submission:delete-{SN[NC.CORRECTIVE_ACTION_PLAN].url_tail.upper()}",
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
                "remove_existing_workbook": reverse(
                    f"report_submission:delete-{SN[NC.ADDITIONAL_UEIS].url_tail}",
                    args=[report_id],
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
                # below URLs handled as a special case because of inconsistent name usage in audit/urls.py and audit/cross_validation/naming.py
                "existing_workbook_url": reverse(
                    f"audit:{SN[NC.SECONDARY_AUDITORS].camel_case}", args=[report_id]
                ),
                "remove_existing_workbook": reverse(
                    f"report_submission:delete-{SN[NC.SECONDARY_AUDITORS].url_tail}",
                    args=[report_id],
                ),
            },
            "additional-eins": {
                "view_id": "additional-eins",
                "view_name": "Additional EINs",
                "instructions": "Enter any additional EINs using the provided worksheet.",
                "DB_id": SN[NC.ADDITIONAL_EINS].snake_case,
                "instructions_url": instructions_base_url + "additional-eins-workbook/",
                "workbook_url": workbook_base_url + "additional-eins-workbook.xlsx",
                # below URLs handled as a special case because of inconsistent name usage in audit/urls.py and audit/cross_validation/naming.py
                "existing_workbook_url": reverse(
                    "audit:AdditionalEins", args=[report_id]
                ),
                "remove_existing_workbook": reverse(
                    f"report_submission:delete-{SN[NC.ADDITIONAL_EINS].url_tail}",
                    args=[report_id],
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


class DeleteFileView(LoginRequiredMixin, View):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.additional_context = {
            "delete-audit-findings": {
                "view_id": "delete-audit-findings",
                "section_name": SN[NC.FINDINGS_UNIFORM_GUIDANCE].friendly_title,
                "field_name": SN[NC.FINDINGS_UNIFORM_GUIDANCE].snake_case,
                "form_section": FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE,
                "event_type": SubmissionEvent.EventType.FINDINGS_UNIFORM_GUIDANCE_DELETED,
            },
            "delete-audit-findings-text": {
                "view_id": "delete-audit-findings-text",
                "section_name": SN[NC.FINDINGS_TEXT].friendly_title,
                "field_name": SN[NC.FINDINGS_TEXT].snake_case,
                "form_section": FORM_SECTIONS.FINDINGS_TEXT,
                "event_type": SubmissionEvent.EventType.FEDERAL_AWARDS_AUDIT_FINDINGS_TEXT_DELETED,
            },
            "delete-cap": {
                "view_id": "delete-cap",
                "section_name": SN[NC.CORRECTIVE_ACTION_PLAN].friendly_title,
                "field_name": SN[NC.CORRECTIVE_ACTION_PLAN].snake_case,
                "form_section": FORM_SECTIONS.CORRECTIVE_ACTION_PLAN,
                "event_type": SubmissionEvent.EventType.CORRECTIVE_ACTION_PLAN_DELETED,
            },
            "delete-additional-ueis": {
                "view_id": "delete-additional-ueis",
                "section_name": SN[NC.ADDITIONAL_UEIS].friendly_title,
                "field_name": SN[NC.ADDITIONAL_UEIS].snake_case,
                "form_section": FORM_SECTIONS.ADDITIONAL_UEIS,
                "event_type": SubmissionEvent.EventType.ADDITIONAL_UEIS_DELETED,
            },
            "delete-secondary-auditors": {
                "view_id": "delete-secondary-auditors",
                "section_name": SN[NC.SECONDARY_AUDITORS].friendly_title,
                "field_name": SN[NC.SECONDARY_AUDITORS].snake_case,
                "form_section": FORM_SECTIONS.SECONDARY_AUDITORS,
                "event_type": SubmissionEvent.EventType.SECONDARY_AUDITORS_DELETED,
            },
            "delete-additional-eins": {
                "view_id": "delete-additional-eins",
                "section_name": SN[NC.ADDITIONAL_EINS].friendly_title,
                "field_name": SN[NC.ADDITIONAL_EINS].snake_case,
                "form_section": FORM_SECTIONS.ADDITIONAL_EINS,
                "event_type": SubmissionEvent.EventType.ADDITIONAL_EINS_DELETED,
            },
        }

    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)

            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                raise PermissionDenied("You do not have access to this audit.")

            # Context for every upload page
            context = {
                "report_id": report_id,
            }
            # Using the current URL, append page specific context
            path_name = request.path.split("/")[2]

            context["view_id"] = self.additional_context[path_name]["view_id"]
            context["section_name"] = self.additional_context[path_name]["section_name"]

            return render(request, "report_submission/delete-file-page.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        try:
            sac = SingleAuditChecklist.objects.get(report_id=report_id)
            accesses = Access.objects.filter(sac=sac, user=request.user)
            if not accesses:
                messages.error(request, "You do not have access to this audit.")
                return redirect(request.path)
            path_name = request.path.split("/")[2]
            section = self.additional_context[path_name]

            try:
                excel_files = ExcelFile.objects.filter(
                    sac=sac, form_section=section["form_section"]
                )
                logger.info(f"Deleting {excel_files.count()} files.")
                excel_files.delete()

                setattr(sac, section["field_name"], None)
                sac.save()
            except ExcelFile.DoesNotExist:
                messages.error(request, "File not found.")
                return redirect(request.path)

            SubmissionEvent.objects.create(
                sac_id=sac.id,
                user=request.user,
                event=section["event_type"],
            )

            logger.info("The file has been successfully deleted.")
            return redirect(f"/audit/submission-progress/{report_id}")

        except SingleAuditChecklist.DoesNotExist:
            logger.error(f"Audit: {report_id} not found")
            messages.error(request, "Audit not found.")
            return redirect(request.path)

        except Exception as e:
            logger.error(f"Unexpected error in DeleteFileView post: {str(e)}")
            messages.error(request, "An unexpected error occurred.")
            return redirect(request.path)
