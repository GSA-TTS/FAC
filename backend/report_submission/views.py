import datetime
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from audit.models import Access, SingleAuditChecklist

import api.views


class ReportSubmissionRedirectView(View):
    def get(self, request):
        return redirect(reverse("eligibility"))


# Step 1
class EligibilityFormView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "report_submission/step-1.html")

    # render eligibility form

    # gather/save step 1 info, redirect to step 2
    def post(self, post_request):
        eligibility = api.views.eligibility_check(post_request.user, post_request.POST)
        if eligibility.get("eligible"):
            return redirect(reverse("auditeeinfo"))

        print("Eligibility data error: ", eligibility)
        return redirect(reverse("eligibility"))


# Step 2
class AuditeeInfoFormView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "report_submission/step-2.html")

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
            return redirect(reverse("auditeeinfo"))
            print("Auditee info data error: ", info_check)

        return redirect(reverse("accessandsubmission"))


# Step 3
class AccessAndSubmissionFormView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, "report_submission/step-3.html")

    # render access-submission form

    # gather/save step 3 info, redirect to step ...4?
    def post(self, post_request):
        result = api.views.access_and_submission_check(
            post_request.user, post_request.POST
        )
        report_id = result.get("report_id")

        if report_id:
            # This should redirect to the commented-out line, but we'll just
            # redirect to the JSON representation of the data until the correct
            # page is up:
            # return redirect(f"/audit/{report_id}")
            return redirect(f"/report_submission/general-information/{report_id}")
        print("Error processing data: ", result)
        return redirect(reverse("accessandsubmission"))


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
                "auditee_contacts": sac.auditee_contacts,
                "report_id": report_id,
            }

            return render(request, "report_submission/gen-form.html", context)
        except SingleAuditChecklist.DoesNotExist:
            raise PermissionDenied("You do not have access to this audit.")

    def post(self, request, *args, **kwargs):
        report_id = kwargs["report_id"]
        sac = SingleAuditChecklist.objects.get(report_id=report_id)

        general_information = {
            "auditee_fiscal_period_end": request.POST.get("auditee_fiscal_period_end"),
            "auditee_fiscal_period_start": request.POST.get(
                "auditee_fiscal_period_start"
            ),
            "audit_period_covered": request.POST.get("audit_period_covered"),
            "ein": request.POST.get("ein"),
            "ein_not_an_ssn_attestation": request.POST.get(
                "ein_not_an_ssn_attestation"
            ),
            "multiple_eins_covered": request.POST.get("multiple_eins_covered"),
            "auditee_uei": request.POST.get("auditee_uei"),
            "multiple_ueis_covered": request.POST.get("multiple_ueis_covered"),
            "auditee_name": request.POST.get("auditee_name"),
            "auditee_address_line_1": request.POST.get("auditee_address_line_1"),
            "auditee_city": request.POST.get("auditee_city"),
            "auditee_state": request.POST.get("auditee_state"),
            "auditee_zip": request.POST.get("auditee_zip"),
            "auditee_contact_name": request.POST.get("auditee_contact_name"),
            "auditee_contact_title": request.POST.get("auditee_contact_title"),
            "auditee_phone": request.POST.get("auditee_phone"),
            "auditee_email": request.POST.get("auditee_email"),
            "user_provided_organization_type": request.POST.get(
                "user_provided_organization_type"
            ),
            "is_usa_based": request.POST.get("is_usa_based"),
            "auditor_firm_name": request.POST.get("auditor_firm_name"),
            "auditor_ein": request.POST.get("auditor_ein"),
            "auditor_ein_not_an_ssn_attestation": request.POST.get(
                "auditor_ein_not_an_ssn_attestation"
            ),
            "auditor_country": request.POST.get("auditor_country"),
            "auditor_address_line_1": request.POST.get("auditor_address_line_1"),
            "auditor_city": request.POST.get("auditor_city"),
            "auditor_state": request.POST.get("auditor_state"),
            "auditor_zip": request.POST.get("auditor_zip"),
            "auditor_contact_name": request.POST.get("auditor_contact_name"),
            "auditor_contact_title": request.POST.get("auditor_contact_title"),
            "auditor_phone": request.POST.get("auditor_phone"),
            "auditor_email": request.POST.get("auditor_email"),
            "auditee_contacts": request.POST.get("auditee_contacts"),
        }

        accesses = Access.objects.filter(sac=sac, user=request.user)
        if not accesses:
            raise Exception("you don't have access to this audit")

        SingleAuditChecklist.objects.filter(pk=sac.id).update(
            general_information=general_information
        )

        return redirect(reverse("audit:MySubmissions"))
