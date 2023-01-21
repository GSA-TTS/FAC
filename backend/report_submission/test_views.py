import json
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponseRedirect
from django.test import RequestFactory, TestCase  # noqa: F401
from django.urls import reverse
from model_bakery import baker


import report_submission.views
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
        +   auditee_name
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
        "met_spending_threshold": True,
        "is_usa_based": True,
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

        response = self.client.post(
            url, data=json.dumps(self.step1_data), content_type="application/json"
        )
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
        url = reverse("eligibility")
        data = {}
        response = self.client.post(
            url, data=json.dumps(data), content_type="application/json"
        )
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

        response = self.client.post(
            step1, data=json.dumps(self.step1_data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/report_submission/auditeeinfo/")

        step2 = reverse("auditeeinfo")
        step2_get = self.client.get(step2)
        self.assertEqual(step2_get.status_code, 200)
        self.assertTemplateUsed(step2_get, "report_submission/step-base.html")
        self.assertTemplateUsed(step2_get, "report_submission/step-2.html")

        step2_data = {
            "auditee_name": "Federal Bureau of Control",
            "auditee_fiscal_period_start": "2022-01-01",
            "auditee_fiscal_period_end": "2023-01-01",
        }
        step2_post = self.client.post(
            step2, data=json.dumps(step2_data), content_type="application/json"
        )
        self.assertEqual(step2_post.status_code, 302)
        self.assertEqual(step2_post.url, "/report_submission/accessandsubmission/")

        step3 = reverse("accessandsubmission")
        step3_get = self.client.get(step3)
        self.assertEqual(step3_get.status_code, 200)
        self.assertTemplateUsed(step3_get, "report_submission/step-base.html")
        self.assertTemplateUsed(step3_get, "report_submission/step-3.html")
        step3_data = {
            "certifying_auditee_contact": "plausible@legit-nonprofit.com",
            "certifying_auditor_contact": "cpa@audits2go.com",
            "auditee_contacts": ["who-me@legit-nonprofit.com"],
            "auditor_contacts": ["good-cook@audits2go.com"],
        }
        step3_post = self.client.post(
            step3, data=json.dumps(step3_data), content_type="application/json"
        )
        self.assertEqual(step3_post.status_code, 302)
        self.assertEqual(step3_post.url[:10], "/sac/edit/")
        report_id = step3_post.url[10:]

        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        combined = self.step1_data | step2_data
        for k in combined:
            self.assertEqual(combined[k], getattr(sac, k))

        accesses = Access.objects.filter(sac=sac)
        for key, val in step3_data.items():
            if key in ("auditee_contacts", "auditor_contacts"):
                # Role is singular even though field is plural:
                role = key[:-1]
                for email in val:
                    matches = [acc for acc in accesses if acc.email == email]
                    self.assertEqual(matches[0].role, role)
            else:
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

    def test_parse_body_data(self):
        expected_output = {
            # "csrfmiddlewaretoken": tk,
            "user_provided_organization_type": "state",
            "met_spending_threshold": True,
            "is_usa_based": True,
        }

        # Test input taken from an example run of submitting step 1
        test_input = bytes(json.dumps(expected_output), encoding="utf-8")

        # Create sample request object
        request = HttpRequest()
        request.method = "POST"
        # Load in the test input. Have to do it in _body as body isn't writable
        request._body = test_input

        # Call function with request
        result = report_submission.views.parse_body_data(request.body)

        self.assertEqual(result, expected_output)

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
