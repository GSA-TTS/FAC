from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from django.test import Client
from model_bakery import baker

from .views import MySubmissions

User = get_user_model()

SUBMISSIONS_PATH = reverse("MySubmissions")
ACCESS_AND_SUBMISSION_PATH = reverse("accessandsubmission")

VALID_ELIGIBILITY_DATA = {
    "is_usa_based": True,
    "met_spending_threshold": True,
    "user_provided_organization_type": "state",
}

VALID_AUDITEE_INFO_DATA = {
    "auditee_uei": "ZQGGHJH74DW7",
    "auditee_fiscal_period_start": "2021-01-01",
    "auditee_fiscal_period_end": "2022-01-01",
    "auditee_name": "Tester",
}

VALID_ACCESS_AND_SUBMISSION_DATA = {
    "certifying_auditee_contact": "a@a.com",
    "certifying_auditor_contact": "b@b.com",
    "auditee_contacts": ["c@c.com"],
    "auditor_contacts": ["d@d.com"],
}


class MySubmissionsViewTests(TestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.user2 = baker.make(User)

        self.client = Client()
        self.client.force_login(user=self.user)

    def test_no_submissions_returns_empty_list(self):
        data = MySubmissions.fetch_my_subnissions(self.user)
        self.assertEquals(len(data), 0)

    def test_user_with_submissions_should_return_expected_data_columns(self):
        self.user.profile.entry_form_data = (
            VALID_ELIGIBILITY_DATA | VALID_AUDITEE_INFO_DATA
        )
        self.user.profile.save()
        self.client.post(
            ACCESS_AND_SUBMISSION_PATH, VALID_ACCESS_AND_SUBMISSION_DATA, format="json"
        )
        data = MySubmissions.fetch_my_subnissions(self.user)
        self.assertGreater(len(data), 0)

        keys = data[0].keys()
        self.assertTrue("report_id" in keys)
        self.assertTrue("submission_status" in keys)
        self.assertTrue("auditee_uei" in keys)
        self.assertTrue("auditee_name" in keys)
        self.assertTrue("fiscal_year_end_date" in keys)

    def test_user_with_no_submissions_should_return_no_data(self):
        self.user.profile.entry_form_data = (
            VALID_ELIGIBILITY_DATA | VALID_AUDITEE_INFO_DATA
        )
        self.user.profile.save()
        self.client.post(
            ACCESS_AND_SUBMISSION_PATH, VALID_ACCESS_AND_SUBMISSION_DATA, format="json"
        )
        data = MySubmissions.fetch_my_subnissions(self.user2)
        self.assertEquals(len(data), 0)
