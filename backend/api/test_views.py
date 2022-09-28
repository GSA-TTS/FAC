import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

from api.test_uei import valid_uei_results
from api.views import SingleAuditChecklistView, SACViewSet
from audit.models import Access, SingleAuditChecklist

User = get_user_model()

ELIGIBILITY_PATH = reverse("eligibility")
AUDITEE_INFO_PATH = reverse("auditee-info")
ACCESS_AND_SUBMISSION_PATH = reverse("accessandsubmission")
SUBMISSIONS_PATH = reverse("submissions")
ACCESS_LIST_PATH = reverse("access-list")
SAC_LIST_PATH = reverse("sac-list")


VALID_AUDITEE_INFO_DATA = {
    "auditee_uei": "ZQGGHJH74DW7",
    "auditee_fiscal_period_start": "2021-01-01",
    "auditee_fiscal_period_end": "2022-01-01",
    "auditee_name": "Tester",
    "submission_status": "in_progress",
}

VALID_ELIGIBILITY_DATA = {
    "is_usa_based": True,
    "met_spending_threshold": True,
    "user_provided_organization_type": "state",
}

VALID_ACCESS_AND_SUBMISSION_DATA = {
    "certifying_auditee_contact": "a@a.com",
    "certifying_auditor_contact": "b@b.com",
    "auditee_contacts": ["c@c.com"],
    "auditor_contacts": ["d@d.com"],
}

SAMPLE_BASE_SAC_DATA = {
    # 0. Meta data
    "submitted_by": None,
    "date_created": "2022-08-11",
    "submission_status": "in_progress",
    "report_id": "2022ABC1000023",
    # Part 1: General Information
    # Q1 Fiscal Dates
    "auditee_fiscal_period_start": "2021-10-01",
    "auditee_fiscal_period_end": "2022-10-01",
    # Q2 Type of Uniform Guidance Audit
    "audit_type": "single-audit",
    # Q3 Audit Period Covered
    "audit_period_covered": "annual",
    # Q4 Auditee Identification Numbers
    "ein": None,
    "ein_not_an_ssn_attestation": None,
    "multiple_eins_covered": None,
    "auditee_uei": "ZQGGHJH74DW7",
    "multiple_ueis_covered": None,
    # Q5 Auditee Information
    "auditee_name": "Auditee McAudited",
    "auditee_address_line_1": "200 feet into left field",
    "auditee_city": "New York",
    "auditee_state": "NY",
    "auditee_zip": "10451",
    "auditee_contact_name": "Designate Representative",
    "auditee_contact_title": "Lord of Doors",
    "auditee_phone": "5558675309",
    "auditee_email": "auditee.mcaudited@leftfield.com",
    # Q6 Primary Auditor Information
    "user_provided_organization_type": "local",
    "met_spending_threshold": True,
    "is_usa_based": True,
    "auditor_firm_name": "Dollar Audit Store",
    "auditor_ein": None,
    "auditor_ein_not_an_ssn_attestation": None,
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


def omit(remove, d) -> dict:
    """omit(["a"], {"a":1, "b": 2}) => {"b": 2}"""
    return {k: d[k] for k in d if k not in remove}


class EligibilityViewTests(TestCase):
    INELIGIBLE = {
        "is_usa_based": False,
        "met_spending_threshold": True,
        "user_provided_organization_type": "state",
    }

    def test_auth_required(self):
        """Unauthenticated requests return unauthorized response"""
        client = APIClient()
        response = client.post(ELIGIBILITY_PATH, VALID_ELIGIBILITY_DATA, format="json")
        self.assertEqual(response.status_code, 401)

    def test_success_and_failure(self):
        """
        An authenticated request receives an eligible response and an ineligible response
        """
        client = APIClient()
        user = baker.make(User)
        client.force_authenticate(user=user)

        response = client.post(ELIGIBILITY_PATH, VALID_ELIGIBILITY_DATA, format="json")
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["eligible"], True)

        response = client.post(ELIGIBILITY_PATH, self.INELIGIBLE, format="json")
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["eligible"], False)


class UEIValidationViewTests(TestCase):
    PATH = reverse("uei-validation")
    SUCCESS = {"auditee_uei": "ZQGGHJH74DW7"}
    INELIGIBLE = {"auditee_uei": "000000000OI*"}

    def test_auth_required(self):
        """Unauthenticated requests return unauthorized response"""
        client = APIClient()
        response = client.post(self.PATH, self.SUCCESS, format="json")
        self.assertEqual(response.status_code, 401)

    def test_success_and_failure(self):
        """
        An authenticated request receives an eligible response and an ineligible response
        """
        client = APIClient()
        user = baker.make(User)
        client.force_authenticate(user=user)

        # Valid
        with patch("api.uei.requests.get") as mock_get:
            mock_get.return_value.status_code = 200  # Mock the status code
            mock_get.return_value.json.return_value = json.loads(
                valid_uei_results
            )  # Mock the json

            response = client.post(self.PATH, self.SUCCESS, format="json")
            data = response.json()
            valid_uei_results_json_entity = json.loads(valid_uei_results)["entityData"][
                0
            ]["entityRegistration"]
            valid_uei_results_json_coredata = json.loads(valid_uei_results)[
                "entityData"
            ][0]["coreData"]

            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["valid"], True)
            self.assertEqual(
                data["response"]["auditee_uei"], valid_uei_results_json_entity["ueiSAM"]
            )
            self.assertEqual(
                data["response"]["auditee_name"],
                valid_uei_results_json_entity["legalBusinessName"],
            )
            self.assertEqual(
                data["response"]["auditee_fiscal_year_end_date"],
                valid_uei_results_json_coredata["entityInformation"][
                    "fiscalYearEndCloseDate"
                ],
            )
            self.assertEqual(
                data["response"]["auditee_address_line_1"],
                valid_uei_results_json_coredata["mailingAddress"]["addressLine1"],
            )
            self.assertEqual(
                data["response"]["auditee_city"],
                valid_uei_results_json_coredata["mailingAddress"]["city"],
            )
            self.assertEqual(
                data["response"]["auditee_state"],
                valid_uei_results_json_coredata["mailingAddress"][
                    "stateOrProvinceCode"
                ],
            )
            self.assertEqual(
                data["response"]["auditee_zip"],
                valid_uei_results_json_coredata["mailingAddress"]["zipCode"],
            )

        response = client.post(self.PATH, self.INELIGIBLE, format="json")
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["valid"], False)


class AuditeeInfoTests(TestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_missing_expected_form_data_from_prior_step(self):
        """Return an error and point to Eligibility step if we're missing data from that step in the user's profile"""
        response = self.client.post(
            AUDITEE_INFO_PATH, VALID_AUDITEE_INFO_DATA, format="json"
        )
        data = response.json()
        self.assertEqual(data["next"], ELIGIBILITY_PATH)
        self.assertTrue(data["errors"])

    def test_valid_data_updates_profile(self):
        """Valid POST update user's form data stored in their profile"""
        # Add eligibility data to profile
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()

        response = self.client.post(
            AUDITEE_INFO_PATH, VALID_AUDITEE_INFO_DATA, format="json"
        )
        data = response.json()
        self.assertEqual(data["next"], ACCESS_AND_SUBMISSION_PATH)
        self.assertEqual(
            self.user.profile.entry_form_data,
            VALID_ELIGIBILITY_DATA | VALID_AUDITEE_INFO_DATA,
        )

    def test_null_auditee_uei(self):
        """
        Auditee UEI can be null
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA | {"auditee_uei": None}
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertEqual(data["next"], ACCESS_AND_SUBMISSION_PATH)
        self.assertEqual(
            self.user.profile.entry_form_data, VALID_ELIGIBILITY_DATA | input_data
        )

    def test_blank_auditee_uei(self):
        """
        Auditee UEI can be blank
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA | {"auditee_uei": ""}
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertEqual(data["next"], ACCESS_AND_SUBMISSION_PATH)
        self.assertEqual(
            self.user.profile.entry_form_data, VALID_ELIGIBILITY_DATA | input_data
        )

    def test_missing_auditee_uei(self):
        """
        Auditee UEI can be missing
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA.copy()
        del input_data["auditee_uei"]
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertEqual(data["next"], ACCESS_AND_SUBMISSION_PATH)
        self.assertEqual(
            self.user.profile.entry_form_data, VALID_ELIGIBILITY_DATA | input_data
        )

    def test_blank_auditee_name(self):
        """
        Auditee name can be blank
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA | {"auditee_name": ""}
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertEqual(data["next"], ACCESS_AND_SUBMISSION_PATH)
        self.assertEqual(
            self.user.profile.entry_form_data, VALID_ELIGIBILITY_DATA | input_data
        )

    def test_null_auditee_name(self):
        """
        Auditee name can be null
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA | {"auditee_name": None}
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertEqual(data["next"], ACCESS_AND_SUBMISSION_PATH)
        self.assertEqual(
            self.user.profile.entry_form_data, VALID_ELIGIBILITY_DATA | input_data
        )

    def test_missing_auditee_name(self):
        """
        Auditee name can be missing
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA.copy()
        del input_data["auditee_name"]
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertEqual(data["next"], ACCESS_AND_SUBMISSION_PATH)
        self.assertEqual(
            self.user.profile.entry_form_data, VALID_ELIGIBILITY_DATA | input_data
        )

    def test_missing_auditee_fiscal_period_start(self):
        """
        Auditee fiscal period start cannot be missing
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA.copy()
        del input_data["auditee_fiscal_period_start"]
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertTrue(data["errors"])

    def test_missing_auditee_fiscal_period_end(self):
        """
        Auditee fiscal period end cannot be missing
        """
        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()
        input_data = VALID_AUDITEE_INFO_DATA.copy()
        del input_data["auditee_fiscal_period_end"]
        response = self.client.post(AUDITEE_INFO_PATH, input_data, format="json")
        data = response.json()
        self.assertTrue(data["errors"])


class AccessAndSubmissionTests(TestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_missing_expected_form_data_from_prior_steps(self):
        """Return an error and point to Eligibility step if we're missing data from any prior step"""
        # Missing Eligibility data
        response = self.client.post(
            ACCESS_AND_SUBMISSION_PATH, VALID_ACCESS_AND_SUBMISSION_DATA, format="json"
        )
        data = response.json()
        self.assertEqual(data["next"], ELIGIBILITY_PATH)
        self.assertTrue(data["errors"])

        self.user.profile.entry_form_data = VALID_ELIGIBILITY_DATA
        self.user.profile.save()

        # Have eligibility, but missing auditee info data
        response = self.client.post(
            ACCESS_AND_SUBMISSION_PATH, VALID_ACCESS_AND_SUBMISSION_DATA, format="json"
        )
        data = response.json()
        self.assertEqual(data["next"], ELIGIBILITY_PATH)
        self.assertTrue(data["errors"])

    def test_valid_data_creates_SAC_and_Access(self):
        """A new SAC is created along with related Access instances"""
        # Add eligibility and Auditee Info data to profile
        self.user.profile.entry_form_data = (
            VALID_ELIGIBILITY_DATA | VALID_AUDITEE_INFO_DATA
        )
        self.user.profile.save()

        response = self.client.post(
            ACCESS_AND_SUBMISSION_PATH, VALID_ACCESS_AND_SUBMISSION_DATA, format="json"
        )
        data = response.json()

        sac = SingleAuditChecklist.objects.get(id=data["sac_id"])

        creator_access = Access.objects.get(sac=sac, role="creator")
        certifying_auditee_contact_access = Access.objects.get(
            sac=sac, role="certifying_auditee_contact"
        )
        certifying_auditor_contact_access = Access.objects.get(
            sac=sac, role="certifying_auditor_contact"
        )
        auditee_contacts_access = Access.objects.filter(sac=sac, role="auditee_contact")
        auditor_contacts_access = Access.objects.filter(sac=sac, role="auditor_contact")

        self.assertEqual(creator_access.user, self.user)
        self.assertEqual(creator_access.email, self.user.email)
        self.assertEqual(certifying_auditee_contact_access.email, "a@a.com")
        self.assertEqual(certifying_auditor_contact_access.email, "b@b.com")
        self.assertEqual(auditee_contacts_access.first().email, "c@c.com")
        self.assertEqual(auditor_contacts_access.first().email, "d@d.com")

    def test_multiple_auditee_auditor_contacts(self):
        """A new SAC is created along with related Access instances"""
        # Add eligibility and Auditee Info data to profile
        self.user.profile.entry_form_data = (
            VALID_ELIGIBILITY_DATA | VALID_AUDITEE_INFO_DATA
        )
        self.user.profile.save()

        access_and_submission_data = VALID_ACCESS_AND_SUBMISSION_DATA.copy()
        access_and_submission_data["auditee_contacts"].append("e@e.com")
        access_and_submission_data["auditor_contacts"].append("f@f.com")

        response = self.client.post(
            ACCESS_AND_SUBMISSION_PATH, access_and_submission_data, format="json"
        )
        data = response.json()

        sac = SingleAuditChecklist.objects.get(id=data["sac_id"])

        auditee_contacts = (
            Access.objects.filter(sac=sac, role="auditee_contact")
            .values_list("email", flat=True)
            .order_by("email")
        )
        auditor_contacts = (
            Access.objects.filter(sac=sac, role="auditor_contact")
            .values_list("email", flat=True)
            .order_by("email")
        )

        self.assertListEqual(
            list(auditee_contacts), access_and_submission_data["auditee_contacts"]
        )
        self.assertListEqual(
            list(auditor_contacts), access_and_submission_data["auditor_contacts"]
        )

    def test_invalid_eligibility_data(self):
        """
        Handle missing data.
        """
        self.user.profile.entry_form_data = (
            VALID_ELIGIBILITY_DATA | VALID_AUDITEE_INFO_DATA
        )
        self.user.profile.save()
        response = self.client.post(ACCESS_AND_SUBMISSION_PATH, {}, format="json")
        data = response.json()
        self.assertEqual(
            data.get("errors", [])["certifying_auditee_contact"][0],
            "This field is required.",
        )
        self.assertEqual(
            data.get("errors", [])["certifying_auditor_contact"][0],
            "This field is required.",
        )
        self.assertEqual(
            data.get("errors", [])["auditee_contacts"][0], "This field is required."
        )
        self.assertEqual(
            data.get("errors", [])["auditor_contacts"][0], "This field is required."
        )


class SACCreationTests(TestCase):
    """Integration tests covering all submission steps leading up to and including creation of a SingleAuditChecklist instance"""

    def setUp(self):
        self.user = baker.make(User)
        self.client = APIClient()

    def test_valid_data_across_steps_creates_an_sac(self):
        """Upon submitting valid data and following `next` responses, a new SAC is created"""
        self.client.force_authenticate(user=self.user)

        # Submit eligibility data
        eligibility_info = {
            "is_usa_based": True,
            "met_spending_threshold": True,
            "user_provided_organization_type": "state",
        }
        response = self.client.post(ELIGIBILITY_PATH, eligibility_info, format="json")
        data = response.json()
        next_step = data["next"]

        # Submit auditee info
        response = self.client.post(next_step, VALID_AUDITEE_INFO_DATA, format="json")
        data = response.json()
        next_step = data["next"]

        # Submit AccessAndSubmission details
        access_and_submission_data = {
            "certifying_auditee_contact": "a@a.com",
            "certifying_auditor_contact": "b@b.com",
            "auditor_contacts": ["c@c.com"],
            "auditee_contacts": ["e@e.com"],
        }
        response = self.client.post(
            next_step, access_and_submission_data, format="json"
        )
        data = response.json()
        sac = SingleAuditChecklist.objects.get(id=data["sac_id"])
        self.assertEqual(sac.submitted_by, self.user)
        self.assertEqual(sac.auditee_uei, "ZQGGHJH74DW7")
        self.assertEqual(sac.submission_status, "in_progress")

        # We also need to verify that the response from the POST includes all
        # the fields we expect, including the data that’s actually stored in
        # Access objects related to this SAC instance.


class SingleAuditChecklistViewTests(TestCase):
    """
    Tests for /sac/edit/[report_id]
    """

    def setUp(self):
        self.user = baker.make(User)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def path(self, report_id):
        """Convenience method to get the path for a report_id)"""
        return reverse("singleauditchecklist", kwargs={"report_id": report_id})

    def test_valid_data_across_steps_is_returned_in_get(self):
        """
        After submitting the valid data and creating an SAC object, we return
        all of the relevant data on GET.
        """
        self.client.force_authenticate(user=self.user)

        # Submit eligibility data
        eligibility_info = {
            "is_usa_based": True,
            "met_spending_threshold": True,
            "user_provided_organization_type": "state",
        }
        response = self.client.post(ELIGIBILITY_PATH, eligibility_info, format="json")
        data = response.json()
        next_step = data["next"]

        # Submit auditee info
        response = self.client.post(next_step, VALID_AUDITEE_INFO_DATA, format="json")
        data = response.json()
        next_step = data["next"]

        # Submit AccessAndSubmission details
        access_and_submission_data = {
            "certifying_auditee_contact": "x@x.com",
            "certifying_auditor_contact": "y@y.com",
            "auditor_contacts": ["z@z.com"],
            "auditee_contacts": ["w@w.com"],
        }
        response = self.client.post(
            next_step, access_and_submission_data, format="json"
        )
        data = response.json()
        sac = SingleAuditChecklist.objects.get(id=data["sac_id"])
        response = self.client.get(self.path(sac.report_id))
        full_data = response.json()
        for key, value in access_and_submission_data.items():
            self.assertEqual(full_data[key], value)
        for key, value in eligibility_info.items():
            self.assertEqual(full_data[key], value)
        for key, value in VALID_AUDITEE_INFO_DATA.items():
            self.assertEqual(full_data[key], value)

    def test_get_authentication_required(self):
        """
        If a request is not authenticated, it should be rejected with a 401
        """

        # use a different client that doesn't authenticate
        client = APIClient()

        response = client.get(self.path("test-report-id"), format="json")

        self.assertEqual(response.status_code, 401)

    def test_get_no_audit_access(self):
        """
        If a user doesn't have an Access object for the SAC, they should get a
        403.
        """
        sac = baker.make(SingleAuditChecklist)

        response = self.client.get(self.path(sac.report_id))
        self.assertEqual(response.status_code, 403)

    def test_get_audit_access(self):
        """
        If a user has an Access object for the SAC, they should get a 200.
        """
        access = baker.make(Access, user=self.user)
        response = self.client.get(self.path(access.sac.report_id))

        self.assertEqual(response.status_code, 200)

    def test_get_bad_report_id(self):
        """
        If the user is logged in and the report ID doesn't match a SAC, they should get a 404.
        """
        response = self.client.get(self.path("nonsensical_id"))

        self.assertEqual(response.status_code, 404)

    def test_put_authentication_required(self):
        """
        If a request is not authenticated, it should be rejected with a 401
        """

        # use a different client that doesn't authenticate
        client = APIClient()

        response = client.put(self.path("test-report-id"), data={}, format="json")

        self.assertEqual(response.status_code, 401)

    def test_put_no_audit_access(self):
        """
        If a user doesn't have an Access object for the SAC, they should get a 403
        """
        sac = baker.make(SingleAuditChecklist)

        response = self.client.put(self.path(sac.report_id), data={}, format="json")

        self.assertEqual(response.status_code, 403)

    def test_put_bad_report_id(self):
        """
        If the user is logged in and the report ID doesn't match a SAC, they should get a 404
        """
        response = self.client.put(self.path("nonsensical_id"))

        self.assertEqual(response.status_code, 404)

    def test_put_bad_data(self):
        """
        If we have edit access and we're submitting to the allowed fields but
        we're submitting bad data, we should get errors.
        """

        def check_response(bad_data, expected):
            sac = baker.make(SingleAuditChecklist)
            access = baker.make(Access, user=self.user, sac=sac)
            path = self.path(access.sac.report_id)
            response = self.client.put(path, bad_data, format="json")
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), expected)

        email_keys = ["auditee_email", "auditor_email"]

        boolean_keys = ["met_spending_threshold", "is_usa_based"]

        choice_keys = [
            "audit_type",
            "audit_period_covered",
            "user_provided_organization_type",
        ]

        ternary_keys = [
            "ein_not_an_ssn_attestation",
            "multiple_eins_covered",
            "multiple_ueis_covered",
            "auditor_ein_not_an_ssn_attestation",
        ]

        length_100_keys = [
            "auditee_contact_name",
            "auditee_contact_title",
            "auditee_phone",
            "auditor_country",
            "auditor_address_line_1",
            "auditor_city",
            "auditor_state",
            "auditor_zip",
            "auditor_contact_name",
            "auditor_contact_title",
            "auditor_phone",
        ]

        test_cases = [
            (
                {
                    "auditee_email": "invalid_email",
                    "auditor_email": "invalid_email",
                },
                {
                    "errors": {
                        "auditee_email": ["Enter a valid email address."],
                        "auditor_email": ["Enter a valid email address."],
                    }
                },
            ),
        ]

        for key in email_keys:
            expected = {"errors": {key: ["Enter a valid email address."]}}
            with self.subTest():
                check_response({key: "invalid_email"}, expected)

        for key in boolean_keys:
            message = "“invalid_boolean” value must be either True or False."
            expected = {"errors": {key: [message]}}
            with self.subTest():
                check_response({key: "invalid_boolean"}, expected)

        for key in choice_keys:
            message = "Value 'invalid_choice' is not a valid choice."
            expected = {"errors": {key: [message]}}
            with self.subTest():
                check_response({key: "invalid_choice"}, expected)

        for key in ternary_keys:
            message = "“invalid_boolean” value must be either True, False, or None."
            expected = {"errors": {key: [message]}}
            with self.subTest():
                check_response({key: "invalid_boolean"}, expected)

        for key in length_100_keys:
            one = "a value over one hundred characters long is annoying to enter "
            two = "succinctly when your Python line length limit is eighty-eight"
            value = f"{one}{two}"
            message = "Ensure this value has at most 100 characters (it has 123)."
            expected = {"errors": {key: [message]}}
            with self.subTest():
                check_response({key: value}, expected)

        for bad_data, expected in test_cases:
            with self.subTest():
                check_response(bad_data, expected)

    def test_put_edit_appropriate_fields(self):
        """
        If we submit data for the appropriate fields, we succeed and also
        update those fields.

        If a field is absent we don't do anything to it.
        """
        test_cases = [
            ({"auditee_phone": "5558675308"}, {"auditee_phone": "5558675309"}),
            (
                {"auditee_email": "before@param.com"},
                {"auditee_email": "after@param.com"},
            ),
            (
                {"auditee_email": "before@param.com"},
                {"auditee_email": "after@param.com"},
            ),
            (
                {
                    "auditee_phone": "5558675308",
                    "auditee_email": "before@param.com",
                },
                {"auditee_email": "after@param.com", "auditee_phone": "5558675309"},
            ),
        ]

        for before, after in test_cases:
            with self.subTest():
                to_remove = ["report_id", "submitted_by"]
                prior = omit(to_remove, SAMPLE_BASE_SAC_DATA | before)

                sac = baker.make(SingleAuditChecklist, submitted_by=self.user, **prior)
                access = baker.make(Access, user=self.user, sac=sac)

                path = self.path(access.sac.report_id)
                response = self.client.put(path, after, format="json")
                self.assertEqual(response.status_code, 200)

                updated_sac = SingleAuditChecklist.objects.get(pk=sac.id)

                for key, value in after.items():
                    self.assertEqual(getattr(updated_sac, key), value)
                    self.assertEqual(response.json()[key], value)

        # Not testing auditee_uei here because baker doesn't know how to follow
        # the rules for it and because we're not supposed to change it via this
        # view anyway.
        to_generate = [k for k in SAMPLE_BASE_SAC_DATA if k not in ["auditee_uei"]]
        base = baker.make(
            SingleAuditChecklist, submitted_by=self.user, _fill_optional=to_generate
        )
        access = baker.make(Access, user=self.user, sac=base)

        data = omit(SingleAuditChecklistView.invalid_keys, SAMPLE_BASE_SAC_DATA)
        path = self.path(access.sac.report_id)
        response = self.client.put(path, data, format="json")
        self.assertEqual(response.status_code, 200)

        sac_data = response.json()
        updated_sac = SingleAuditChecklist.objects.get(pk=base.id)

        for key, value in data.items():
            self.assertEqual(getattr(updated_sac, key), value)
            self.assertEqual(sac_data[key], value)

    def test_edit_inappropriate_fields(self):
        """
        If we submit data for fields that can't be edited, we reject the PUT
        and return errors.
        """

        test_cases = [
            (
                {"report_id": "5558675308"},
                {
                    "errors": "The following fields cannot be modified via this endpoint: report_id."
                },
            ),
            (
                {"report_id": "5558675308", "auditee_uei": "5558675308"},
                {
                    "errors": "The following fields cannot be modified via this endpoint: auditee_uei, report_id."
                },
            ),
        ]
        for invalid_key in SingleAuditChecklistView.invalid_keys:
            test_case = (
                {invalid_key: "whatever"},
                {
                    "errors": f"The following fields cannot be modified via this endpoint: {invalid_key}."
                },
            )
            test_cases.append(test_case)

        for data, expected in test_cases:
            with self.subTest():
                sac = baker.make(SingleAuditChecklist)
                access = baker.make(Access, user=self.user, sac=sac)
                path = self.path(access.sac.report_id)
                response = self.client.put(path, data, format="json")

                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json(), expected)


class SacFederalAwardsViewTests(TestCase):
    """
    Tests for /sac/edit/[report_id]/federal_awards
    """

    def setUp(self):
        self.user = baker.make(User)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Submit eligibility data
        eligibility_info = {
            "is_usa_based": True,
            "met_spending_threshold": True,
            "user_provided_organization_type": "state",
        }
        response = self.client.post(ELIGIBILITY_PATH, eligibility_info, format="json")
        data = response.json()
        next_step = data["next"]

        # Submit auditee info
        response = self.client.post(next_step, VALID_AUDITEE_INFO_DATA, format="json")
        data = response.json()
        next_step = data["next"]

        # Submit AccessAndSubmission details
        response = self.client.post(
            next_step, VALID_ACCESS_AND_SUBMISSION_DATA, format="json"
        )

        # Report details to be used for tests
        self.sac_data = response.json()
        self.sac_report_id = self.sac_data["sac_id"]

    def path(self, report_id):
        """Convenience method to get the path for a report_id)"""
        return reverse("sacfederalawards", kwargs={"report_id": self.sac_report_id})

    def test_get_authentication_required(self):
        """
        If a request is not authenticated, it should be rejected with a 401
        """

        # use a different client that doesn't authenticate
        client = APIClient()
        response = client.get(self.path(self.sac_report_id), format="json")
        self.assertEqual(response.status_code, 401)

    def test_get_no_audit_awards_access(self):
        """
        If a user doesn't have an Access object for the SAC, they should get a
        403.
        """
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)
        # sac.submitted_by = user

        response = self.client.get(self.path(sac.report_id))
        self.assertEqual(response.status_code, 403)

    def test_get_valid_placeholder_data(self):
        """
        If the federal awards endpoint is hit, (for now) it should return an empty object
        """

        # SAC created in setUp().
        response = self.client.get(self.path(self.sac_report_id))
        data = response.json()
        self.assertEqual(data, {})


class SubmissionsViewTests(TestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_no_submissions_returns_empty_list(self):
        response = self.client.get(SUBMISSIONS_PATH, format="json")
        data = response.json()
        self.assertEqual(data, [])

    def test_user_with_submissions_should_return_expected_data_columns(self):
        self.user.profile.entry_form_data = (
            VALID_ELIGIBILITY_DATA | VALID_AUDITEE_INFO_DATA
        )
        self.user.profile.save()
        self.client.post(
            ACCESS_AND_SUBMISSION_PATH, VALID_ACCESS_AND_SUBMISSION_DATA, format="json"
        )

        response = self.client.get(SUBMISSIONS_PATH, format="json")

        data = response.json()
        self.assertTrue("report_id" in data[0])
        self.assertEqual(
            data[0]["submission_status"],
            VALID_AUDITEE_INFO_DATA["submission_status"],
        )
        self.assertEqual(
            data[0]["auditee_uei"],
            VALID_AUDITEE_INFO_DATA["auditee_uei"],
        )
        self.assertEqual(
            data[0]["auditee_fiscal_period_end"],
            VALID_AUDITEE_INFO_DATA["auditee_fiscal_period_end"],
        )
        self.assertEqual(
            data[0]["auditee_name"],
            VALID_AUDITEE_INFO_DATA["auditee_name"],
        )
        self.assertEqual(
            len(data[0]),
            5,
        )


class AccessListViewTests(TestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_authentication_required(self):
        """
        If a request is not authenticated, it should be rejected with a 401
        """

        # use a different client that doesn't authenticate
        client = APIClient()

        response = client.get(ACCESS_LIST_PATH, format="json")

        self.assertEqual(response.status_code, 401)

    def test_no_access_returns_empty_list(self):
        """
        If a user does not have access to any audits, an empty list is returned
        """
        response = self.client.get(ACCESS_LIST_PATH, format="json")
        data = response.json()

        self.assertEqual(data, [])

    def test_single_access_returns_expected(self):
        """
        If a user has acccess to a single audit, only that audit is returned
        """
        access = baker.make(Access, user=self.user)

        response = self.client.get(ACCESS_LIST_PATH, format="json")
        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["role"], access.role)
        self.assertEqual(data[0]["report_id"], access.sac.report_id)

    def test_multiple_access_returns_expected(self):
        """
        If a user has access to multiple audits, all are returned
        """
        access_1 = baker.make(Access, user=self.user)
        access_2 = baker.make(Access, user=self.user)

        response = self.client.get(ACCESS_LIST_PATH, format="json")
        data = response.json()

        self.assertEqual(len(data), 2)

        data_1 = next((a for a in data if a["report_id"] == access_1.sac.report_id))

        self.assertEqual(data_1["role"], access_1.role)
        self.assertEqual(data_1["report_id"], access_1.sac.report_id)

        data_2 = next((a for a in data if a["report_id"] == access_2.sac.report_id))

        self.assertEqual(data_2["role"], access_2.role)
        self.assertEqual(data_2["report_id"], access_2.sac.report_id)

    def test_multiple_roles_returns_expected(self):
        """
        If a user has multiple roles for an audit, that audit is returned one time for each role
        """
        sac = baker.make(SingleAuditChecklist)
        baker.make(Access, user=self.user, role="certifying_auditee_contact", sac=sac)
        baker.make(Access, user=self.user, role="creator", sac=sac)

        response = self.client.get(ACCESS_LIST_PATH, format="json")
        data = response.json()

        self.assertEqual(len(data), 2)

        certifying_auditee_contact_accesses = list(
            filter(lambda a: a["role"] == "certifying_auditee_contact", data)
        )
        self.assertEqual(len(certifying_auditee_contact_accesses), 1)
        self.assertEqual(
            certifying_auditee_contact_accesses[0]["report_id"], sac.report_id
        )

        creator_accesses = list(filter(lambda a: a["role"] == "creator", data))
        self.assertEqual(len(creator_accesses), 1)
        self.assertEqual(creator_accesses[0]["report_id"], sac.report_id)

    def test_deleted_sac_not_returned(self):
        """
        If a user has their SACs deleted, it is no longer returned in their access list
        """
        sac = baker.make(SingleAuditChecklist)
        access_1 = baker.make(Access, user=self.user)
        baker.make(Access, user=self.user, sac=sac)

        response_1 = self.client.get(ACCESS_LIST_PATH, format="json")
        data_1 = response_1.json()

        # initially we see both in our access list
        self.assertEqual(len(data_1), 2)

        # now delete one access_2
        sac.delete()

        response_2 = self.client.get(ACCESS_LIST_PATH, format="json")
        data_2 = response_2.json()

        # only the one remaining access should come back
        self.assertEqual(len(data_2), 1)
        self.assertEqual(data_2[0]["report_id"], access_1.sac.report_id)

    def test_deleted_access_not_returned(self):
        """
        If a user has their Access deleted, the associated SAC is no longer returned in their access list
        """
        access_1 = baker.make(Access, user=self.user)
        access_2 = baker.make(Access, user=self.user)

        response_1 = self.client.get(ACCESS_LIST_PATH, format="json")
        data_1 = response_1.json()

        # initially we see both in our access list
        self.assertEqual(len(data_1), 2)

        # now delete one access_2
        access_2.delete()

        response_2 = self.client.get(ACCESS_LIST_PATH, format="json")
        data_2 = response_2.json()

        # only the one remaining access should come back
        self.assertEqual(len(data_2), 1)
        self.assertEqual(data_2[0]["report_id"], access_1.sac.report_id)


class SACViewSetTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_no_auth_required(self):
        """
        The SACViewSet should not require authentication or permissions
        """
        self.assertEqual(SACViewSet.authentication_classes, [])
        self.assertEqual(SACViewSet.permission_classes, [])

    def test_list_no_audits_returns_empty_list(self):
        """
        If there are no SACs in the database, the list endpoint should return no results
        """
        response = self.client.get(SAC_LIST_PATH)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [])

    def test_list_none_submitted_returns_empty_list(self):
        """
        If there are SACs in the database, but none which have a status of subnmitted, the list endpoint shoul return no results
        """
        for status in SingleAuditChecklist.STATUSES:
            if status[0] != "submitted":
                baker.make(
                    SingleAuditChecklist, _quantity=100, submission_status=status[0]
                )

        response = self.client.get(SAC_LIST_PATH)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, [])

    def test_list_returns_only_submitted(self):
        """
        If there are SACs in the database, only those with a submission_status of "submitted" should be returned
        """
        for status in SingleAuditChecklist.STATUSES:
            baker.make(SingleAuditChecklist, _quantity=100, submission_status=status[0])

        response = self.client.get(SAC_LIST_PATH)
        data = response.json()

        self.assertEqual(len(data), 100)
        self.assertTrue(
            all(audit["submission_status"] == "submitted" for audit in data)
        )

    def test_detail_no_match_returns_404(self):
        """
        If there is no SAC matching the provided report_id, the detail endpoint should return 404
        """
        url = reverse("sac-detail", kwargs={"report_id": "not-a-real-report-id"})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_detail_match_submitted_returns_sac(self):
        """
        If there is a SAC matching the provided report_id, and the SAC has a submission_status of submitted, the detail endpoint should return the SAC
        """
        report_id = "test-report-id"
        sac = baker.make(
            SingleAuditChecklist, report_id=report_id, submission_status="submitted"
        )

        url = reverse("sac-detail", kwargs={"report_id": report_id})

        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data, sac)

    def test_detail_match_unsubmitted_returns_404(self):
        """
        If there is a SAC matching the provided report_id, and the SAC has a submission_status other than submitted, the detail endpoint should return a 404
        """
        for status in SingleAuditChecklist.STATUSES:
            with self.subTest():
                if status[0] != "submitted":
                    report_id = f"id-{status[0]}"
                    baker.make(
                        SingleAuditChecklist,
                        report_id=report_id,
                        submission_status=status[0],
                    )

                    url = reverse("sac-detail", kwargs={"report_id": report_id})

                    response = self.client.get(url)

                    self.assertEqual(response.status_code, 404)
