import datetime
import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import BadRequest, PermissionDenied, ValidationError
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View

from audit.models import Access, SingleAuditChecklist, LateChangeError
from audit.validators import validate_general_information_json

from report_submission.forms import GeneralInformationForm

import api.views

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

        print("Eligibility data error: ", eligibility)
        return redirect(reverse("report_submission:eligibility"))


# Step 2
class AuditeeInfoFormView(LoginRequiredMixin, View):
    def get(self, request):
        args = {}
        args["step"] = 2
        return render(request, "report_submission/step-2.html", args)

    # render auditee info form

    # gather/save step 2 info, redirect to step 3
    def post(self, post_request):
        # TODO: Wrap in better error-checking
        start = datetime.datetime.strptime(
            post_request.POST.get("auditee_fiscal_period_start", "01/01/1970"),
            "%m/%d/%Y",
        )
        end = datetime.datetime.strptime(
            post_request.POST.get("auditee_fiscal_period_end", "01/01/1970"),
            "%m/%d/%Y",
        )

        formatted_post = {
            "csrfmiddlewaretoken": post_request.POST.get("csrfmiddlewaretoken"),
            "auditee_uei": post_request.POST.get("auditee_uei"),
            "auditee_name": post_request.POST.get("auditee_name"),
            "auditee_address_line_1": post_request.POST.get("auditee_address_line_1"),
            "auditee_city": post_request.POST.get("auditee_city"),
            "auditee_state": post_request.POST.get("auditee_state"),
            "auditee_zip": post_request.POST.get("auditee_zip"),
            "auditee_fiscal_period_start": start.strftime("%Y-%m-%d"),
            "auditee_fiscal_period_end": end.strftime("%Y-%m-%d"),
        }

        info_check = api.views.auditee_info_check(post_request.user, formatted_post)
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
        print("Error processing data: ", result)
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
                "auditor_address_line_1": sac.auditor_address_line_1,
                "auditor_city": sac.auditor_city,
                "auditor_state": sac.auditor_state,
                "auditor_zip": sac.auditor_zip,
                "auditor_contact_name": sac.auditor_contact_name,
                "auditor_contact_title": sac.auditor_contact_title,
                "auditor_phone": sac.auditor_phone,
                "auditor_email": sac.auditor_email,
                "report_id": report_id,
            }

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

            if form.is_valid():
                general_information = sac.general_information
                logger.info(form.cleaned_data)
                general_information.update(form.cleaned_data)

                validated = validate_general_information_json(general_information)
                sac.general_information = validated
                if general_information.get("audit_type"):
                    sac.audit_type = general_information["audit_type"]
                sac.save()

                return redirect(f"/audit/submission-progress/{report_id}")
        except SingleAuditChecklist.DoesNotExist as err:
            raise PermissionDenied("You do not have access to this audit.") from err
        except ValidationError as err:
            logger.warning(
                "ValidationError for report ID %s: %s", report_id, err.message
            )
        except LateChangeError:
            return render(request, "audit/no-late-changes.html")

        raise BadRequest()


class UploadPageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]

        # Organized by URL name, page specific constants are defined here
        # Data can then be accessed by checking the current URL
        additional_context = {
            "federal-awards": {
                "view_id": "federal-awards",
                "view_name": "Federal awards",
                "instructions": "Enter the federal awards you received in the last audit year using the provided worksheet.",
                "DB_id": "federal_awards",
            },
            "audit-findings": {
                "view_id": "audit-findings",
                "view_name": "Audit findings",
                "instructions": "Enter the audit findings for your federal awards using the provided worksheet.",
                "DB_id": "findings_uniform_guidance",
            },
            "audit-findings-text": {
                "view_id": "audit-findings-text",
                "view_name": "Audit findings text",
                "instructions": "Enter the text for your audit findings using the provided worksheet.",
                "DB_id": "findings_text",
            },
            "CAP": {
                "view_id": "CAP",
                "view_name": "Corrective Action Plan (CAP)",
                "instructions": "Enter your CAP text using the provided worksheet.",
                "DB_id": "corrective_action_plan",
            },
            "additional-EINs": {
                "view_id": "additional-EINs",
                "view_name": "Additional EINs",
                "instructions": "Enter any additional EINs using the provided worksheet.",
            },
            "additional-ueis": {
                "view_id": "additional-ueis",
                "view_name": "Additional UEIs",
                "instructions": "Enter any additional UEIs using the provided worksheet.",
            },
            "secondary-auditors": {
                "view_id": "secondary-auditors",
                "view_name": "Secondary auditors",
                "instructions": "Enter any additional auditors using the provided worksheet.",
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
