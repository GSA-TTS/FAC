import json
from datetime import datetime

from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker

from audit.models import Access, SingleAuditChecklist


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
