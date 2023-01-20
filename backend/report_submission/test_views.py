from django.contrib import auth
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponseRedirect
from django.test import RequestFactory, TestCase  # noqa: F401
from django.urls import reverse
from model_bakery import baker

from rest_framework.test import APIClient

import report_submission.views

class TestViews(TestCase):

    # def setUp(self):
    #     None

    def test_parse_body_data(self):
        expected_output = {
                'csrfmiddlewaretoken': 'T6ECt7xJsKB6JGH301QTorauTmXTvPndTv7lhT8Mm8dN4SpJX9h9hqBdTGgTdmVN',
                'user_provided_organization_type': 'state',
                'met_spending_threshold': True,
                'is_usa_based': True
            }

        # Test input taken from an example run of submitting step 1
        test_input = b'{"csrfmiddlewaretoken":"T6ECt7xJsKB6JGH301QTorauTmXTvPndTv7lhT8Mm8dN4SpJX9h9hqBdTGgTdmVN","user_provided_organization_type":"state","met_spending_threshold":true,"is_usa_based":true}'

        # Create sample request object
        request = HttpRequest()
        request.method = 'POST'
        # Load in the test input. Have to do it in _body as body isn't writable
        request._body = test_input

        # Call function with request
        result = report_submission.views.parse_body_data(request.body)

        self.assertEqual(result, expected_output)

    def test_reportsubmissionredirectview_get_redirects(self):
        url = reverse("report_submission")

        response = self.client.get(url)
        # Expect /report_submission/ to redirect to /report_submission/eligibility/
        self.assertRedirects(response, reverse("eligibility"), target_status_code=302, fetch_redirect_response=False)

    def test_eligibilityformview_get_requires_login(self):
        user = baker.make(User)

        url = reverse("eligibility")
        response = self.client.get(url)

        # Should redirect to login page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue("openid/login" in response.url)


    def test_eligibilityformview_get_template(self):
        user = baker.make(User)
        self.client.force_login(user)

        url = reverse("eligibility")
        response = self.client.get(url)

        self.assertTrue(user.is_authenticated)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "report_submission/step-base.html")
        self.assertTemplateUsed(response, "report_submission/step-1.html")

