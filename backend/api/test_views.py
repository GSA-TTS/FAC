import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

from api.test_uei import valid_uei_results
from api.views import SingleAuditChecklistView
from audit.models import Access, SingleAuditChecklist

User = get_user_model()

ELIGIBILITY_PATH = reverse("eligibility")
AUDITEE_INFO_PATH = reverse("auditee-info")
ACCESS_AND_SUBMISSION_PATH = reverse("accessandsubmission")
SUBMISSIONS_PATH = reverse("submissions")
ACCESS_LIST_PATH = reverse("access-list")


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
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data["valid"], True)

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
            sac=sac, role="auditee_cert"
        )
        certifying_auditor_contact_access = Access.objects.get(
            sac=sac, role="auditor_cert"
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

    def test_put_edit_appropriate_fields(self):
        """
        If we submit data for the appropriate fields, we succeed and also
        update those fields.

        If a field is absent we don't do anything to it.

        TODO: add test cases above for all of the fields.
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

        updated_sac = SingleAuditChecklist.objects.get(pk=base.id)

        for key, value in data.items():
            self.assertEqual(getattr(updated_sac, key), value)
            self.assertEqual(response.json()[key], value)

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
        baker.make(Access, user=self.user, role="auditee_cert", sac=sac)
        baker.make(Access, user=self.user, role="creator", sac=sac)

        response = self.client.get(ACCESS_LIST_PATH, format="json")
        data = response.json()

        self.assertEqual(len(data), 2)

        auditee_cert_accesses = list(
            filter(lambda a: a["role"] == "auditee_cert", data)
        )
        self.assertEqual(len(auditee_cert_accesses), 1)
        self.assertEqual(auditee_cert_accesses[0]["report_id"], sac.report_id)

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
