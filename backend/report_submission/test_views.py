import json
from datetime import datetime

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker

from audit.models import Access, SingleAuditChecklist


SAMPLE_BASE_SAC_DATA = {
    # 0. Meta data
    "submitted_by": None,
    "date_created": "2022-08-11",
    "submission_status": "in_progress",
    "report_id": "2022ABC1000023",
    "audit_type": "single-audit",
    # Part 1: General Information
    "general_information": {
        "auditee_fiscal_period_start": "2021-10-01",
        "auditee_fiscal_period_end": "2022-10-01",
        "audit_period_covered": "annual",
        "ein": "123456789",
        "ein_not_an_ssn_attestation": True,
        "multiple_eins_covered": False,
        "auditee_uei": "ZQGGHJH74DW7",
        "multiple_ueis_covered": False,
        "auditee_name": "Auditee McAudited",
        "auditee_address_line_1": "200 feet into left field",
        "auditee_city": "New York",
        "auditee_state": "NY",
        "auditee_zip": "10451",
        "auditee_contact_name": "Designate Representative",
        "auditee_contact_title": "Lord of Doors",
        "auditee_phone": "5558675309",
        "auditee_email": "auditee.mcaudited@leftfield.com",
        "user_provided_organization_type": "local",
        "met_spending_threshold": True,
        "is_usa_based": True,
        "auditor_firm_name": "Dollar Audit Store",
        "auditor_ein": "123456789",
        "auditor_ein_not_an_ssn_attestation": True,
        "auditor_country": "USA",
        "auditor_address_line_1": "100 Percent Respectable St.",
        "auditor_city": "Podunk",
        "auditor_state": "NY",
        "auditor_zip": "14886",
        "auditor_contact_name": "Qualified Human Accountant",
        "auditor_contact_title": "Just an ordinary person",
        "auditor_phone": "0008675309",
        "auditor_email": "qualified.human.accountant@dollarauditstore.com",
    },
}


def omit(remove, d) -> dict:
    """omit(["a"], {"a":1, "b": 2}) => {"b": 2}"""
    return {k: d[k] for k in d if k not in remove}


class TestPreliminaryViews(TestCase):
    """
    Pre-SAC URLs are:

    #.  /report_submissions/eligibility

        +   user_provided_organization_type
        +   met_spending_threshold
        +   is_usa_based
    #.  /report_submission/auditeeinfo

        +   auditee_uei
        +   auditee_name (optional)
        +   auditee_fiscal_period_start
        +   auditee_fiscal_period_end
    #.  /report_submission/accessandsubmission

        +   certifying_auditee_contact
        +   certifying_auditor_contact
        +   auditee_contacts
        +   auditor_contacts

    """

    step1_data = {
        "user_provided_organization_type": "state",
        "met_spending_threshold": "True",
        "is_usa_based": "True",
    }

    step2_data = {
        "auditee_uei": "LW4MXE7SKMV1",
        "auditee_fiscal_period_start": "01/01/2021",
        "auditee_fiscal_period_end": "12/31/2021",
    }

    step3_data = {
        "certifying_auditee_contact": "a@a.com",
        "certifying_auditor_contact": "b@b.com",
        "auditee_contacts": "c@c.com",  # noqa: F601
        "auditee_contacts": "d@d.com",  # noqa: F601
        "auditor_contacts": "e@e.com",  # noqa: F601
        "auditor_contacts": "f@f.com",  # noqa: F601
    }

    def test_step_one_eligibility_submission_pass(self):
        """
        /report_submissions/eligibility
        Check that the correct templates are loaded on GET.
        Check that the POST succeeds with appropriate data.
        """
        user = baker.make(User)
        self.client.force_login(user)
        url = reverse("eligibility")

        get_response = self.client.get(url)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "report_submission/step-base.html")
        self.assertTemplateUsed(get_response, "report_submission/step-1.html")

        response = self.client.post(url, data=self.step1_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/report_submission/auditeeinfo/")
        user.refresh_from_db()
        saved = user.profile.entry_form_data
        self.assertEqual(saved["user_provided_organization_type"], "state")
        self.assertEqual(saved["met_spending_threshold"], "True")
        self.assertEqual(saved["is_usa_based"], "True")

    def test_step_one_eligibility_submission_fail(self):
        """
        /report_submissions/eligibility
        Check that the POST fails when missing data.
        """
        user = baker.make(User)
        self.client.force_login(user)
        url = reverse("eligibility")
        data = {}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/report_submission/eligibility/")

    def test_end_to_end_submission_pass(self):
        """
        Go through all three and verify that we end up with a SAC.
        """
        user = baker.make(User)
        self.client.force_login(user)
        step1 = reverse("eligibility")

        get_response = self.client.get(step1)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "report_submission/step-base.html")
        self.assertTemplateUsed(get_response, "report_submission/step-1.html")

        response = self.client.post(step1, data=self.step1_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/report_submission/auditeeinfo/")

        step2 = reverse("auditeeinfo")
        step2_get = self.client.get(step2)
        self.assertEqual(step2_get.status_code, 200)
        self.assertTemplateUsed(step2_get, "report_submission/step-base.html")
        self.assertTemplateUsed(step2_get, "report_submission/step-2.html")

        step2_data = {
            # "auditee_name": "Federal Bureau of Control",
            "auditee_uei": "KZV2XNZZN3A8",
            "auditee_fiscal_period_start": "01/01/2022",
            "auditee_fiscal_period_end": "01/01/2023",
        }
        step2_post = self.client.post(step2, data=step2_data)
        self.assertEqual(step2_post.status_code, 302)
        self.assertEqual(step2_post.url, "/report_submission/accessandsubmission/")

        step3 = reverse("accessandsubmission")
        step3_get = self.client.get(step3)
        self.assertEqual(step3_get.status_code, 200)
        self.assertTemplateUsed(step3_get, "report_submission/step-base.html")
        self.assertTemplateUsed(step3_get, "report_submission/step-3.html")

        step3_post = self.client.post(step3, data=self.step3_data)

        self.assertEqual(step3_post.status_code, 302)
        self.assertEqual(step3_post.url[:39], "/report_submission/general-information/")
        report_id = step3_post.url[-17:]

        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        combined = self.step1_data | step2_data
        for k in combined:
            # Test bools as strings
            if isinstance(getattr(sac, k), bool):
                self.assertEqual(combined[k], str(getattr(sac, k)))
            # Test start/end dates formatted m/d/Y -> Y-m-d
            elif "fiscal_period" in k:
                combined_date_formatted = datetime.strptime(
                    combined[k], "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
                self.assertEqual(combined_date_formatted, getattr(sac, k))
            # Test everything else normally
            else:
                self.assertEqual(combined[k], getattr(sac, k))

        accesses = Access.objects.filter(sac=sac)
        for key, val in self.step3_data.items():
            if key in ("auditee_contacts", "auditor_contacts"):
                # Role is singular even though field is plural:
                key = key[:-1]
            matches = [acc for acc in accesses if acc.email == val]
            self.assertEqual(matches[0].role, key)

    def test_step_two_auditeeinfo_submission_fail(self):
        """
        /report_submissions/auditeeinfo
        Check that the correct templates are loaded on GET.
        Check that the POST succeeds with appropriate data.
        """
        user = baker.make(User)
        self.client.force_login(user)
        url = reverse("auditeeinfo")

        get_response = self.client.get(url)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "report_submission/step-base.html")
        self.assertTemplateUsed(get_response, "report_submission/step-2.html")

        data = {}
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/report_submission/auditeeinfo/")

    def test_step_three_accessandsubmission_submission_fail(self):
        """
        /report_submissions/accessandsubmission
        Check that the correct templates are loaded on GET.
        Check that the POST succeeds with appropriate data.
        """
        user = baker.make(User)
        self.client.force_login(user)
        url = reverse("accessandsubmission")

        get_response = self.client.get(url)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "report_submission/step-base.html")
        self.assertTemplateUsed(get_response, "report_submission/step-3.html")

        data = {}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/report_submission/accessandsubmission/")

    def test_reportsubmissionredirectview_get_redirects(self):
        url = reverse("report_submission")

        response = self.client.get(url)
        # Expect /report_submission/ to redirect to /report_submission/eligibility/
        self.assertRedirects(
            response,
            reverse("eligibility"),
            target_status_code=302,
            fetch_redirect_response=False,
        )

    def test_eligibilityformview_get_requires_login(self):
        url = reverse("eligibility")
        response = self.client.get(url)

        # Should redirect to login page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue("openid/login" in response.url)

    def test_auditeeinfoformview_get_requires_login(self):
        url = reverse("auditeeinfo")
        response = self.client.get(url)

        # Should redirect to login page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue("openid/login" in response.url)

    def test_accessandsubmissionformview_get_requires_login(self):
        url = reverse("accessandsubmission")
        response = self.client.get(url)

        # Should redirect to login page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue("openid/login" in response.url)


class GeneralInformationFormViewTests(TestCase):
    def test_get_requires_login(self):
        """Requests to the GET endpoint require the user to be authenticated"""
        sac = baker.make(SingleAuditChecklist)

        url = reverse("general_information", kwargs={"report_id": sac.report_id})

        response = self.client.get(url)

        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue("openid/login" in response.url)

    def test_get_bad_report_id_returns_403(self):
        """When a request is made for a malformed or nonexistent report_id, a 403 error should be returned"""
        user = baker.make(User)
        self.client.force_login(user)

        url = reverse(
            "general_information", kwargs={"report_id": "this is not a report id"}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_get_inaccessible_audit_returns_403(self):
        """When a request is made for an audit that is inaccessible for this user, a 403 error should be returned"""
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)

        self.client.force_login(user)

        url = reverse("general_information", kwargs={"report_id": sac.report_id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_get_valid_audit_returns_populated_form(self):
        """When a request is made for an audit that is accessible for this user, a populated general information form should be returned"""
        user = baker.make(User)

        sac_data = omit(["submitted_by"], SAMPLE_BASE_SAC_DATA)
        sac = baker.make(SingleAuditChecklist, submitted_by=user, **sac_data)
        baker.make(Access, user=user, sac=sac)

        self.client.force_login(user)

        url = reverse("general_information", kwargs={"report_id": sac.report_id})

        response = self.client.get(url)

        text_fields = [
            "auditee_fiscal_period_start",
            "auditee_fiscal_period_end",
            "audit_period_covered",
            "auditee_uei",
            "auditee_name",
            "auditee_address_line_1",
            "auditee_city",
            "auditee_state",
            "auditee_zip",
            "auditee_contact_name",
            "auditee_contact_title",
            "auditee_phone",
            "auditee_email",
            "auditor_firm_name",
            "auditor_country",
            "auditor_address_line_1",
            "auditor_city",
            "auditor_state",
            "auditor_zip",
            "auditor_contact_name",
            "auditor_contact_title",
            "auditor_phone",
            "auditor_email",
        ]

        # assert that the text fields are populated in the returned form
        for field in text_fields:
            value = sac.general_information[field]

            self.assertContains(response, f'value="{value}"')

    def test_post_requires_login(self):
        """Requests to the POST endpoint require the user to be authenticated"""
        sac = baker.make(SingleAuditChecklist)

        url = reverse("general_information", kwargs={"report_id": sac.report_id})

        response = self.client.post(url)

        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue("openid/login" in response.url)

    def test_post_bad_report_id_returns_403(self):
        """When a request is made to update for a malformed or nonexistent report_id, a 403 error should be returned"""
        user = baker.make(User)
        self.client.force_login(user)

        url = reverse(
            "general_information", kwargs={"report_id": "this is not a report id"}
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)

    def test_post_inaccessible_audit_returns_403(self):
        """When a request is made for an audit that is inaccessible for this user, a 403 error should be returned"""
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)

        self.client.force_login(user)

        url = reverse("general_information", kwargs={"report_id": sac.report_id})

        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)

    def test_post_updates_fields(self):
        """When the general information form is submitted, the general information fields for the target audit are updated in the database"""
        user = baker.make(User)

        sac_data = omit(["submitted_by"], SAMPLE_BASE_SAC_DATA)
        sac = baker.make(SingleAuditChecklist, submitted_by=user, **sac_data)
        baker.make(Access, user=user, sac=sac)

        self.client.force_login(user)

        url = reverse("general_information", kwargs={"report_id": sac.report_id})

        data = {
            "auditee_fiscal_period_start": "2021-11-01",
            "auditee_fiscal_period_end": "2022-11-01",
            "audit_period_covered": "biennial",
            "ein": "123456780",
            "ein_not_an_ssn_attestation": True,
            "multiple_eins_covered": False,
            "auditee_uei": "ZQGGHJH74DW7",
            "multiple_ueis_covered": False,
            "auditee_name": "Auditee McAudited",
            "auditee_address_line_1": "200 feet into left field",
            "auditee_city": "New York",
            "auditee_state": "NY",
            "auditee_zip": "10451",
            "auditee_contact_name": "Designate Representative",
            "auditee_contact_title": "Lord of Doors",
            "auditee_phone": "5558675309",
            "auditee_email": "auditee.mcaudited@leftfield.com",
            "user_provided_organization_type": "local",
            "met_spending_threshold": True,
            "is_usa_based": True,
            "auditor_firm_name": "Dollar Audit Store",
            "auditor_ein": "123456789",
            "auditor_ein_not_an_ssn_attestation": True,
            "auditor_country": "USA",
            "auditor_address_line_1": "100 Percent Respectable St.",
            "auditor_city": "Podunk",
            "auditor_state": "NY",
            "auditor_zip": "14886",
            "auditor_contact_name": "Qualified Human Accountant",
            "auditor_contact_title": "Just an ordinary person",
            "auditor_phone": "0008675309",
            "auditor_email": "qualified.human.accountant@dollarauditstore.com",
        }

        response = self.client.post(url, data=data)

        updated_sac = SingleAuditChecklist.objects.get(pk=sac.id)

        for field in data:
            self.assertEqual(getattr(updated_sac, field), data[field], f"mismatch for field: {field}")
