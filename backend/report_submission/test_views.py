from datetime import date, datetime, timedelta

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.conf import settings
from unittest.mock import MagicMock, patch
from report_submission.views import DeleteFileView
from model_bakery import baker

from audit.models import Access, SingleAuditChecklist, SubmissionEvent
from django.contrib.messages.storage.fallback import FallbackStorage
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.exceptions import PermissionDenied
from django.contrib.messages import get_messages


def omit(remove, d) -> dict:
    """omit(["a"], {"a":1, "b": 2}) => {"b": 2}"""
    return {k: d[k] for k in d if k not in remove}


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
        "audit_period_covered": "other",
        "audit_period_other_months": "10",
        "ein": "123456789",
        "ein_not_an_ssn_attestation": True,
        "multiple_eins_covered": False,
        "auditee_uei": "zQGGHJH74DW7",
        "multiple_ueis_covered": False,
        "secondary_auditors_exist": True,
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

EMAIL_TO_ROLE = {
    "certifying_auditee_contact_email": "certifying_auditee_contact",
    "certifying_auditor_contact_email": "certifying_auditor_contact",
    "auditee_contacts_email": "editor",
    "auditor_contacts_email": "editor",
}


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

        +   certifying_auditee_contact_fullname
        +   certifying_auditee_contact_email
        +   certifying_auditor_contact_fullname
        +   certifying_auditor_contact_email
        +   auditee_contacts_fullname
        +   auditee_contacts_email
        +   auditor_contacts_fullname
        +   auditor_contacts_email

    """

    step1_data = {
        "user_provided_organization_type": "state",
        "met_spending_threshold": "True",
        "is_usa_based": "True",
    }

    step2_data = {
        "auditee_uei": "D7A4J33FUMJ1",
        "auditee_fiscal_period_start": "2021-01-01",
        "auditee_fiscal_period_end": "2021-12-31",
    }

    step3_data = {
        "certifying_auditee_contact_fullname": "Fuller A. Namesmith",
        "certifying_auditee_contact_email": "a@a.com",
        "certifying_auditor_contact_fullname": "Fuller B. Namesmith",
        "certifying_auditor_contact_email": "b@b.com",
        "auditee_contacts_fullname": "Fuller C. Namesmith",
        "auditee_contacts_email": "c@c.com",
        "auditor_contacts_fullname": "Fuller D. Namesmith",
        "auditor_contacts_email": "d@d.com",
    }

    def test_step_one_eligibility_submission_pass(self):
        """
        /report_submissions/eligibility
        Check that the correct templates are loaded on GET.
        Check that the POST succeeds with appropriate data.
        """
        user = baker.make(User)
        self.client.force_login(user)
        url = reverse("report_submission:eligibility")

        get_response = self.client.get(url)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "report_submission/step-base.html")
        self.assertTemplateUsed(get_response, "report_submission/step-1.html")
        self.assertEqual(
            get_response.context["dollar_thresholds"],
            [
                "$750,000 or more with a Fiscal Year starting BEFORE October 01, 2024",
                "$1,000,000 or more with a Fiscal Year starting ON or AFTER October 01, 2024",
            ],
        )

        response = self.client.post(url, data=self.step1_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/report_submission/auditeeinfo/")
        user.refresh_from_db()
        saved = user.profile.entry_form_data
        self.assertEqual(saved["user_provided_organization_type"], "state")
        self.assertEqual(saved["met_spending_threshold"], True)
        self.assertEqual(saved["is_usa_based"], True)

    def test_step_one_eligibility_submission_fail(self):
        """
        /report_submissions/eligibility
        Check that the POST fails when missing data.
        """
        user = baker.make(User)
        self.client.force_login(user)
        url = reverse("report_submission:eligibility")
        data = {}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/report_submission/eligibility/")

    @patch("report_submission.forms.get_uei_info_from_sam_gov")
    def test_end_to_end_submission_pass(self, mock_get_uei_info):
        """
        Go through all three and verify that we end up with a SAC.
        """
        mock_get_uei_info.return_value = {
            "valid": True,
        }

        user = baker.make(User)
        self.client.force_login(user)
        step1 = reverse("report_submission:eligibility")

        get_response = self.client.get(step1)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "report_submission/step-base.html")
        self.assertTemplateUsed(get_response, "report_submission/step-1.html")

        response = self.client.post(step1, data=self.step1_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/report_submission/auditeeinfo/")

        step2 = reverse("report_submission:auditeeinfo")
        step2_get = self.client.get(step2)
        self.assertEqual(step2_get.status_code, 200)
        self.assertTemplateUsed(step2_get, "report_submission/step-base.html")
        self.assertTemplateUsed(step2_get, "report_submission/step-2.html")

        step2_data = {
            "auditee_uei": "kZV2XNZZN3A8",
            "auditee_fiscal_period_start": "01/01/2022",
            "auditee_fiscal_period_end": "01/01/2023",
        }
        step2_post = self.client.post(step2, data=step2_data)
        self.assertEqual(step2_post.status_code, 302)
        self.assertEqual(step2_post.url, "/report_submission/accessandsubmission/")

        step3 = reverse("report_submission:accessandsubmission")
        step3_get = self.client.get(step3)
        self.assertEqual(step3_get.status_code, 200)
        self.assertTemplateUsed(step3_get, "report_submission/step-base.html")
        self.assertTemplateUsed(step3_get, "report_submission/step-3.html")

        step3_post = self.client.post(step3, data=self.step3_data)

        self.assertEqual(step3_post.status_code, 302)
        path_segments = step3_post.url.split("/")
        self.assertEqual(
            "/".join(path_segments[:3]), "/report_submission/general-information"
        )
        report_id = path_segments[-1]

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
            elif k == "auditee_uei":
                self.assertEqual(combined[k].upper(), getattr(sac, k))
            else:
                self.assertEqual(combined[k], getattr(sac, k))

        accesses = Access.objects.filter(sac=sac)
        for key, val in self.step3_data.items():
            # Fields come in as auditee/auditor emails, become roles:
            if key in (
                "auditee_contacts_email",
                "auditor_contacts_email",
                "certifying_auditee_contact_email",
                "certifying_auditor_contact_email",
            ):
                key = EMAIL_TO_ROLE[key]
                matches = [acc for acc in accesses if acc.email == val]
                self.assertEqual(matches[0].role, key)

    @patch("report_submission.forms.get_uei_info_from_sam_gov")
    def test_step_two_auditeeinfo_submission_empty(self, mock_get_uei_info):
        """
        /report_submissions/auditeeinfo
        Check that the correct templates are loaded on GET.
        Check that the POST fails with an empty data payload
        """
        mock_get_uei_info.return_value = {
            "valid": True,
        }

        user = baker.make(User)
        user.profile.entry_form_data = self.step1_data
        user.profile.save()
        self.client.force_login(user)
        url = reverse("report_submission:auditeeinfo")

        get_response = self.client.get(url)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "report_submission/step-base.html")
        self.assertTemplateUsed(get_response, "report_submission/step-2.html")

        data = {}
        response = self.client.post(
            url,
            data=data,
        )
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.context["form"].errors["auditee_uei"], ["This field is required."]
        )
        self.assertListEqual(
            response.context["form"].errors["auditee_fiscal_period_start"],
            ["This field is required."],
        )
        self.assertListEqual(
            response.context["form"].errors["auditee_fiscal_period_end"],
            ["This field is required."],
        )

    @patch("report_submission.forms.get_uei_info_from_sam_gov")
    def test_step_two_auditeeinfo_invalid_dates(self, mock_get_uei_info):
        """
        Check that the server validates that start date preceeds end date
        """
        mock_get_uei_info.return_value = {"valid": True}

        user = baker.make(User)
        user.profile.entry_form_data = self.step1_data
        user.profile.save()
        self.client.force_login(user)
        url = reverse("report_submission:auditeeinfo")

        get_response = self.client.get(url)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "report_submission/step-base.html")
        self.assertTemplateUsed(get_response, "report_submission/step-2.html")

        data = {
            "auditee_uei": "ZqGGHJH74DW7",
            "auditee_fiscal_period_start": "2023-08-31",
            "auditee_fiscal_period_end": "2023-08-01",
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)

        errors = response.context["form"].non_field_errors()
        self.assertListEqual(
            errors,
            [
                "Auditee fiscal period end date must be later than auditee fiscal period start date"
            ],
        )

    @patch("report_submission.forms.get_uei_info_from_sam_gov")
    def test_step_two_auditeeinfo_future_enddate(self, mock_get_uei_info):
        """
        Check that the server validates that end date preceeds current date
        """
        mock_get_uei_info.return_value = {"valid": True}

        user = baker.make(User)
        user.profile.entry_form_data = self.step1_data
        user.profile.save()
        self.client.force_login(user)
        url = reverse("report_submission:auditeeinfo")

        get_response = self.client.get(url)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "report_submission/step-base.html")
        self.assertTemplateUsed(get_response, "report_submission/step-2.html")

        tomorrow = date.today() + timedelta(days=1)

        data = {
            "auditee_uei": "ZqGGHJH74DW7",
            "auditee_fiscal_period_start": "2023-08-31",
            "auditee_fiscal_period_end": tomorrow.strftime("%Y-%m-%d"),
        }
        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 200)

        errors = response.context["form"].non_field_errors()
        self.assertListEqual(
            errors,
            ["Auditee fiscal period dates must be earlier than today"],
        )

    def test_step_three_accessandsubmission_submission_fail(self):
        """
        /report_submissions/accessandsubmission
        Check that the correct templates are loaded on GET.
        Check that the POST succeeds with appropriate data.
        """
        user = baker.make(User)
        user.profile.entry_form_data = {
            **self.step1_data,
            **self.step2_data,
            **self.step3_data,
        }
        user.profile.save()
        self.client.force_login(user)
        url = reverse("report_submission:accessandsubmission")

        get_response = self.client.get(url)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(get_response.status_code, 200)
        self.assertTemplateUsed(get_response, "report_submission/step-base.html")
        self.assertTemplateUsed(get_response, "report_submission/step-3.html")

        data = {}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 400)

    def test_reportsubmissionredirectview_get_redirects(self):
        url = reverse("report_submission:report_submission")

        response = self.client.get(url)
        # Expect /report_submission/ to redirect to /report_submission/eligibility/
        self.assertRedirects(
            response,
            reverse("report_submission:eligibility"),
            target_status_code=302,
            fetch_redirect_response=False,
        )

    def test_eligibilityformview_get_requires_login(self):
        url = reverse("report_submission:eligibility")
        response = self.client.get(url)

        # Should redirect to login page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue("openid/login" in response.url)

    def test_auditeeinfoformview_get_requires_login(self):
        url = reverse("report_submission:auditeeinfo")
        response = self.client.get(url)

        # Should redirect to login page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue("openid/login" in response.url)

    def test_accessandsubmissionformview_get_requires_login(self):
        url = reverse("report_submission:accessandsubmission")
        response = self.client.get(url)

        # Should redirect to login page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue("openid/login" in response.url)

    def test_auditeeinfo_no_eligibility(self):
        user = baker.make(User)
        user.profile.entry_form_data = {
            **self.step1_data,
            "is_usa_based": False,  # Ineligible
        }
        user.profile.save()
        self.client.force_login(user)

        url = reverse("report_submission:auditeeinfo")
        response = self.client.get(url)

        # Should redirect to step 1 page due to no eligibility
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue("report_submission/eligibility" in response.url)

    def test_accessandsubmission_no_auditee_info(self):
        user = baker.make(User)
        user.profile.entry_form_data = self.step1_data
        user.profile.save()
        self.client.force_login(user)

        url = reverse("report_submission:accessandsubmission")
        response = self.client.get(url)

        # Should redirect to step 2 page since auditee info isn't present
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue("report_submission/auditeeinfo" in response.url)


class GeneralInformationFormViewTests(TestCase):
    def test_get_requires_login(self):
        """Requests to the GET endpoint require the user to be authenticated"""
        sac = baker.make(SingleAuditChecklist)

        url = reverse(
            "report_submission:general_information", kwargs={"report_id": sac.report_id}
        )

        response = self.client.get(url)

        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue("openid/login" in response.url)

    def test_get_bad_report_id_returns_403(self):
        """When a request is made for a malformed or nonexistent report_id, a 403 error should be returned"""
        user = baker.make(User)
        self.client.force_login(user)

        url = reverse(
            "report_submission:general_information",
            kwargs={"report_id": "this is not a report id"},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_get_inaccessible_audit_returns_403(self):
        """When a request is made for an audit that is inaccessible for this user, a 403 error should be returned"""
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)

        self.client.force_login(user)

        url = reverse(
            "report_submission:general_information", kwargs={"report_id": sac.report_id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_get_valid_audit_returns_populated_form(self):
        """When a request is made for an audit that is accessible for this user, a populated general information form should be returned"""
        user = baker.make(User)

        sac_data = omit(["submitted_by"], SAMPLE_BASE_SAC_DATA)
        sac = baker.make(SingleAuditChecklist, submitted_by=user, **sac_data)
        baker.make(Access, user=user, sac=sac)

        self.client.force_login(user)

        url = reverse(
            "report_submission:general_information", kwargs={"report_id": sac.report_id}
        )

        response = self.client.get(url)

        text_fields = [
            "auditee_fiscal_period_start",
            "auditee_fiscal_period_end",
            "audit_period_covered",
            "audit_period_other_months",
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
            if (
                field != "auditee_fiscal_period_start"
                and field != "auditee_fiscal_period_end"
            ):
                value = sac.general_information[field]
                self.assertEqual(response.context[field], value)
            else:
                # These are stored in YYYY-MM-DD but get sent as MM/DD/YYYY, so they get special treatment.
                stored_value = sac.general_information[field]
                formatted_field = datetime.strptime(
                    response.context[field], "%m/%d/%Y"
                ).strftime("%Y-%m-%d")
                self.assertEqual(stored_value, formatted_field)

    def test_post_requires_login(self):
        """Requests to the POST endpoint require the user to be authenticated"""
        sac = baker.make(SingleAuditChecklist)

        url = reverse(
            "report_submission:general_information", kwargs={"report_id": sac.report_id}
        )

        response = self.client.post(url)

        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue("openid/login" in response.url)

    def test_post_bad_report_id_returns_403(self):
        """When a request is made to update for a malformed or nonexistent report_id, a 403 error should be returned"""
        user = baker.make(User)
        self.client.force_login(user)

        url = reverse(
            "report_submission:general_information",
            kwargs={"report_id": "this is not a report id"},
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)

    def test_post_inaccessible_audit_returns_403(self):
        """When a request is made for an audit that is inaccessible for this user, a 403 error should be returned"""
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)

        self.client.force_login(user)

        url = reverse(
            "report_submission:general_information", kwargs={"report_id": sac.report_id}
        )

        response = self.client.post(url)

        self.assertEqual(response.status_code, 403)

    def test_post_updates_fields_for_foreign_auditor(self):
        self.test_post_updates_fields(foreign_auditor=True)

    def test_post_updates_fields(self, foreign_auditor=False):
        """When the general information form is submitted, the general information fields for the target audit are updated in the database"""
        user = baker.make(User)

        sac_data = omit(["submitted_by"], SAMPLE_BASE_SAC_DATA)
        sac = baker.make(SingleAuditChecklist, submitted_by=user, **sac_data)
        baker.make(Access, user=user, sac=sac)

        self.client.force_login(user)

        url = reverse(
            "report_submission:general_information", kwargs={"report_id": sac.report_id}
        )

        data = {
            "audit_type": "single-audit",
            "auditee_fiscal_period_start": "11/01/2021",
            "auditee_fiscal_period_end": "11/01/2022",
            "audit_period_covered": "other",
            "audit_period_other_months": "10",
            "ein": "123456780",
            "ein_not_an_ssn_attestation": True,
            "multiple_eins_covered": True,
            "auditee_uei": "ZQGGHJH74DW8",
            "multiple_ueis_covered": True,
            "secondary_auditors_exist": True,
            "auditee_name": "Auditee McAudited again",
            "auditee_address_line_1": "500 feet into left field",
            "auditee_city": "Chicago",
            "auditee_state": "IL",
            "auditee_zip": "60640",
            "auditee_contact_name": "Updated Designated Representative",
            "auditee_contact_title": "Lord of Windows",
            "auditee_phone": "5558675310",
            "auditee_email": "auditee.mcaudited.again@leftfield.com",
            "auditor_firm_name": "Penny Audit Store",
            "auditor_ein": "123456780",
            "auditor_ein_not_an_ssn_attestation": True,
            "auditor_contact_name": "Qualified Robot Accountant",
            "auditor_contact_title": "Just an extraordinary person",
            "auditor_phone": "9876543210",
            "auditor_email": "qualified.robot.accountant@dollarauditstore.com",
        }
        if foreign_auditor:
            data.update(
                {
                    "auditor_country": "non-USA",
                    "auditor_international_address": "10 Downing St London, England",
                }
            )
        else:
            data.update(
                {
                    "auditor_country": "USA",
                    "auditor_address_line_1": "100 Percent Respectable Rd.",
                    "auditor_city": "Not Podunk",
                    "auditor_state": "IL",
                    "auditor_zip": "60604",
                }
            )

        response = self.client.post(url, data=data)

        self.assertEqual(response.status_code, 302)

        updated_sac = SingleAuditChecklist.objects.get(pk=sac.id)

        for field in data:
            if field == "auditee_uei":
                self.assertEqual(
                    getattr(updated_sac, field),
                    data[field].upper(),
                    f"mismatch for field: {field}",
                )
            if field not in (
                "auditee_fiscal_period_start",
                "auditee_fiscal_period_end",
            ):
                self.assertEqual(
                    getattr(updated_sac, field),
                    data[field],
                    f"mismatch for field: {field}",
                )
            else:
                # These are stored in YYYY-MM-DD but are sent as MM/DD/YYYY, so they get special treatment.
                stored_value = getattr(updated_sac, field)
                formatted_field = datetime.strptime(data[field], "%m/%d/%Y").strftime(
                    "%Y-%m-%d"
                )
                self.assertEqual(
                    stored_value, formatted_field, f"mismatch for field: {field}"
                )

        submission_events = SubmissionEvent.objects.filter(sac=sac)

        # the most recent event should be GENERAL_INFORMATION_UPDATED
        event_count = len(submission_events)
        self.assertGreaterEqual(event_count, 1)
        self.assertEqual(
            submission_events[event_count - 1].event,
            SubmissionEvent.EventType.GENERAL_INFORMATION_UPDATED,
        )

    def test_post_requires_fields(self):
        """If there are fields missing from the submitted form, the submission should be rejected"""
        user = baker.make(User)

        sac_data = omit(["submitted_by"], SAMPLE_BASE_SAC_DATA)
        sac = baker.make(SingleAuditChecklist, submitted_by=user, **sac_data)
        baker.make(Access, user=user, sac=sac)

        self.client.force_login(user)

        url = reverse(
            "report_submission:general_information", kwargs={"report_id": sac.report_id}
        )

        # submit a bad date format for auditee_fiscal_period_start to verify that the input is being validated
        data = {
            "auditee_fiscal_period_start": "Not a date",
        }

        # Post will redirect back to the page with an error message above the relevant date field
        response = self.client.post(url, data=data)

        self.assertContains(response, "Dates should be in the format")

    def test_post_gsa_migration_error(self):
        """If GSA_MIGRATION is present as an email, the submission should be rejected"""
        user = baker.make(User)

        sac_data = omit(["submitted_by"], SAMPLE_BASE_SAC_DATA)
        sac = baker.make(SingleAuditChecklist, submitted_by=user, **sac_data)
        baker.make(Access, user=user, sac=sac)

        self.client.force_login(user)

        url = reverse(
            "report_submission:general_information", kwargs={"report_id": sac.report_id}
        )

        data = {
            "audit_type": "single-audit",
            "auditee_fiscal_period_start": "11/01/2021",
            "auditee_fiscal_period_end": "11/01/2022",
            "audit_period_covered": "other",
            "audit_period_other_months": "10",
            "ein": "123456780",
            "ein_not_an_ssn_attestation": True,
            "multiple_eins_covered": True,
            "auditee_uei": "ZQGGHJH74DW8",
            "multiple_ueis_covered": True,
            "secondary_auditors_exist": True,
            "auditee_name": "Auditee McAudited again",
            "auditee_address_line_1": "500 feet into left field",
            "auditee_city": "Chicago",
            "auditee_state": "IL",
            "auditee_zip": "60640",
            "auditor_international_address": "",
            "auditee_contact_name": "Updated Designated Representative",
            "auditee_contact_title": "Lord of Windows",
            "auditee_phone": "5558675310",
            "auditee_email": settings.GSA_MIGRATION,  # Not allowed
            "auditor_firm_name": "Penny Audit Store",
            "auditor_ein": "123456780",
            "auditor_ein_not_an_ssn_attestation": True,
            "auditor_contact_name": "Qualified Robot Accountant",
            "auditor_contact_title": "Just an extraordinary person",
            "auditor_phone": "9876543210",
            "auditor_email": settings.GSA_MIGRATION,  # Not allowed
        }

        response = self.client.post(url, data=data)

        self.assertIn("errors", response.context)
        self.assertIn(
            "Enter a valid email address.",
            response.context["errors"],
        )

    def test_post_validates_general_information(self):
        """When the general information form is submitted, the data should be validated against the general information schema"""
        user = baker.make(User)

        sac_data = omit(["submitted_by"], SAMPLE_BASE_SAC_DATA)
        sac = baker.make(SingleAuditChecklist, submitted_by=user, **sac_data)
        baker.make(Access, user=user, sac=sac)

        self.client.force_login(user)

        url = reverse(
            "report_submission:general_information", kwargs={"report_id": sac.report_id}
        )

        # submit a bad date format for auditee_fiscal_period_start to verify that the input is being validated
        data = {
            "auditee_fiscal_period_start": "not a date",
            "auditee_fiscal_period_end": "2022-11-01",
            "audit_period_covered": "biennial",
            "ein": "123456780",
            "ein_not_an_ssn_attestation": True,
            "multiple_eins_covered": False,
            "auditee_uei": "ZQGGhJH74DW8",
            "multiple_ueis_covered": False,
            "secondary_auditors_exist": True,
            "auditee_name": "Auditee McAudited again",
            "auditee_address_line_1": "500 feet into left field",
            "auditee_city": "Chicago",
            "auditee_state": "IL",
            "auditee_zip": "60640",
            "auditee_contact_name": "Updated Designated Representative",
            "auditee_contact_title": "Lord of Windows",
            "auditee_phone": "5558675310",
            "auditee_email": "auditee.mcaudited.again@leftfield.com",
            "user_provided_organization_type": "state",
            "auditor_firm_name": "Penny Audit Store",
            "auditor_ein": "123456780",
            "auditor_ein_not_an_ssn_attestation": True,
            "auditor_country": "UK",
            "auditor_address_line_1": "100 Percent Respectable Rd.",
            "auditor_city": "Not Podunk",
            "auditor_state": "IL",
            "auditor_zip": "60604",
            "auditor_contact_name": "Qualified Robot Accountant",
            "auditor_contact_title": "Just an extraordinary person",
            "auditor_phone": "0008675310",
            "auditor_email": "qualified.robot.accountant@dollarauditstore.com",
        }

        # Post will redirect back to the page with an error message above the relevant date field
        response = self.client.post(url, data=data)

        self.assertContains(response, "Dates should be in the format")
        self.assertNotIn(
            "GSA_MIGRATION not permitted outside of migrations",
            response.context["errors"],
        )


def add_session_to_request(request):
    """Middleware to add session to request."""
    middleware = SessionMiddleware(lambda x: x)
    middleware.process_request(request)
    request.session.save()


def add_messages_to_request(request):
    """Attach a message storage to the request."""
    setattr(request, "_messages", FallbackStorage(request))


class DeleteFileViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
            username="user", password="password"
        )  # nosec
        self.view = DeleteFileView()
        self.report_id = "12345"
        self.path_name = "delete-audit-findings"
        self.url = reverse(
            "report_submission:audit-findings-text",
            kwargs={"report_id": self.report_id},
        )

    def make_request(self, method="get"):
        if method.lower() == "post":
            request = self.factory.post(self.url)
        else:
            request = self.factory.get(self.url)
        request.user = self.user
        request.path = "/delete/" + self.path_name + "/"
        add_session_to_request(request)
        add_messages_to_request(request)
        return request

    def test_get_no_access(self):
        request = self.make_request("get")
        with patch("audit.models.SingleAuditChecklist.objects.get") as mock_get:
            mock_get.side_effect = SingleAuditChecklist.DoesNotExist
            with self.assertRaises(PermissionDenied):
                self.view.get(request, report_id=self.report_id)

    def test_get_successful_render(self):
        sac = MagicMock(report_id=self.report_id)
        access = MagicMock(user=self.user)
        request = self.make_request("get")

        with patch("audit.models.SingleAuditChecklist.objects.get", return_value=sac):
            with patch("audit.models.Access.objects.filter", return_value=[access]):
                response = self.view.get(request, report_id=self.report_id)
                self.assertEqual(response.status_code, 200)
                self.assertIn("delete-audit-findings", response.content.decode())

    def test_post_no_access(self):
        request = self.factory.post(self.url)
        request.user = self.user
        request.path = "/delete/" + self.path_name + "/"
        request = self.make_request("get")

        with patch("audit.models.SingleAuditChecklist.objects.get"):
            with patch("audit.models.Access.objects.filter", return_value=[]):
                response = self.view.post(request, report_id=self.report_id)
                self.assertEqual(response.status_code, 302)

        messages = [message.message for message in get_messages(request)]
        self.assertIn("You do not have access to this audit.", messages)

    def test_post_file_deletion_successful(self):
        sac = MagicMock(report_id=self.report_id)
        access = MagicMock(user=self.user)
        request = self.factory.post(self.url)
        request.user = self.user
        request.path = "/delete/" + self.path_name + "/"
        request = self.make_request("get")

        with patch("audit.models.SingleAuditChecklist.objects.get", return_value=sac):
            with patch("audit.models.Access.objects.filter", return_value=[access]):
                with patch("audit.models.ExcelFile.objects.filter") as mock_filter:
                    mock_files = MagicMock()
                    mock_filter.return_value = mock_files
                    mock_files.count.return_value = 1

                    response = self.view.post(request, report_id=self.report_id)
                    self.assertEqual(response.status_code, 302)
                    mock_files.delete.assert_called_once()

    def test_post_unexpected_error(self):
        request = self.factory.post(self.url)
        request.user = self.user
        request.path = "/delete/" + self.path_name + "/"
        request = self.make_request("get")

        with patch("audit.models.SingleAuditChecklist.objects.get") as mock_get:
            mock_get.side_effect = Exception("Unexpected error")
            response = self.view.post(request, report_id=self.report_id)
            self.assertEqual(response.status_code, 302)
        messages = [message.message for message in get_messages(request)]
        self.assertIn("An unexpected error occurred.", messages)
