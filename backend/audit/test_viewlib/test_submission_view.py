import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from audit.cross_validation.naming import SECTION_NAMES as SN
from audit.fixtures.excel import FORM_SECTIONS
from audit.fixtures.single_audit_checklist import (
    fake_auditee_certification,
    fake_auditor_certification,
)
from audit.models import (
    Access,
    Audit,
    SingleAuditChecklist,
    SingleAuditReportFile,
    generate_sac_report_id,
)
from audit.models.constants import SAC_SEQUENCE_ID, STATUS, RESUBMISSION_STATUS
from audit.models.utils import get_next_sequence_id
from audit.utils import FORM_SECTION_HANDLERS
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from faker import Faker
from model_bakery import baker

User = get_user_model()

AUDIT_JSON_FIXTURES = Path(__file__).parent.parent / "fixtures" / "json"
STATUSES = STATUS


def _load_json(target):
    """Given a str or Path, load JSON from that target."""
    raw = Path(target).read_text(encoding="utf-8")
    return json.loads(raw)


def _load_json_audit_data(file, section):
    json = _load_json(AUDIT_JSON_FIXTURES / file)
    return FORM_SECTION_HANDLERS.get(section)["audit_object"](json)


def _client_post(client, view_str, kwargs=None, data=None):
    """Helper function for POST requests (does not force auth)"""
    kwargs, data = kwargs or {}, data or {}
    url = reverse(view_str, kwargs=kwargs)
    return client.post(url, data=data)


def _authed_post(client, user, view_str, kwargs=None, data=None):
    """Helper function for POST requests (forces auth)"""
    client.force_login(user=user)
    return _client_post(client, view_str, kwargs, data)


def _make_user_and_sac(**kwargs):
    """Helper function for to make a user and basic sac"""
    user = baker.make(User)
    sac = baker.make(SingleAuditChecklist, **kwargs)
    return user, sac


def _make_user_and_audit(report_id, audit_data):
    """Helper function for to make a user and basic audit"""
    user = baker.make(User)
    audit_data = audit_data or {}
    audit = baker.make(Audit, report_id=report_id, version=0, audit=audit_data)
    return user, audit


def _mock_gen_report_id(sequence):
    """Helper function for generate a sac report id"""
    return generate_sac_report_id(
        sequence=sequence, end_date=datetime.now().date().isoformat()
    )


def _build_auditor_cert_dict(certification: dict, signature: dict) -> dict:
    """Helper function for building a dictionary for auditor certification"""
    return {
        "auditor_certification": certification,
        "auditor_signature": signature,
    }


def _build_auditee_cert_dict(certification: dict, signature: dict) -> dict:
    """Helper function for building a dictionary for auditee certification"""
    return {
        "auditee_certification": certification,
        "auditee_signature": signature,
    }


def _just_uei(uei, fieldname):
    """
    _just_uei("whatever", "additional_eins") returns:
        {
            "AdditionalEINs": {"auditee_uei": "whatever"}
        }

    Given a UEI (a string) and a fieldname in
    audit.cross_validation.naming.SECTION_NAMES, return a structure with the camel-case
    version of that fieldname as the key and {"auditee_uei": uei} as the value.
    """
    return {SN[fieldname].camel_case: {"auditee_uei": uei}}


def _just_uei_workbooks(uei):
    """
    Given a UEI (a string), returns a dict containing all of the workbook snake_case
    field names with a value of {CamelCaseFieldName: {"auditee_uei": uei}} for each
    of those fields.
    """
    workbooks = {k: v for k, v in SN.items() if v.workbook_number}
    return {k: _just_uei(uei, k) for k in workbooks}


def _fake_audit_information():
    # TODO: consolidate all fixtures! This is a copy of a fixture from
    # intake_to_dissemination, which is not ideal.
    fake = Faker()

    return {
        "dollar_threshold": 10345.45,
        "gaap_results": json.dumps([fake.word()]),
        "is_going_concern_included": "Y" if fake.boolean() else "N",
        "is_internal_control_deficiency_disclosed": "Y" if fake.boolean() else "N",
        "is_internal_control_material_weakness_disclosed": (
            "Y" if fake.boolean() else "N"
        ),
        "is_material_noncompliance_disclosed": "Y" if fake.boolean() else "N",
        "is_aicpa_audit_guide_included": "Y" if fake.boolean() else "N",
        "is_low_risk_auditee": "Y" if fake.boolean() else "N",
        "agencies": json.dumps([fake.word()]),
    }


class SubmissionViewTests(TestCase):
    """
    Testing for the final step: submitting.
    """

    def setUp(self):
        """Set up test client, user, SAC, and URL"""
        awardsfile = "federal-awards--test0001test--simple-pass.json"

        self.client = Client()
        self.user = baker.make(User)
        self.audit = baker.make(
            Audit,
            version=0,
            audit={**_load_json_audit_data(awardsfile, FORM_SECTIONS.FEDERAL_AWARDS)},
        )
        self.sac = baker.make(
            SingleAuditChecklist,
            submission_status=STATUS.AUDITEE_CERTIFIED,
            report_id=self.audit.report_id,
        )
        self.url = reverse(
            "audit:Submission", kwargs={"report_id": self.audit.report_id}
        )
        self.client.force_login(self.user)
        baker.make(
            "audit.Access",
            sac=self.sac,
            user=self.user,
            role="certifying_auditee_contact",
        )

    def test_get_renders_template(self):
        """Test that GET renders the submission template with correct context"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "audit/submission.html")
        self.assertIn("report_id", response.context)
        self.assertIn("submission_status", response.context)
        self.assertEqual(response.context["report_id"], self.sac.report_id)
        self.assertEqual(
            response.context["submission_status"], self.sac.submission_status
        )

    def test_get_permission_denied_if_no_sac(self):
        """Test that GET returns 403 if SAC does not exist"""
        invalid_url = reverse("audit:Submission", kwargs={"report_id": "INVALID"})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 403)

    @patch("audit.models.SingleAuditChecklist.validate_full")
    @patch("audit.models.Audit.validate")
    @patch("audit.views.submissions.sac_transition")
    @patch("audit.views.submissions.remove_workbook_artifacts")
    @patch("audit.views.submissions.SingleAuditChecklist.disseminate")
    def test_post_successful(
        self,
        mock_disseminate,
        mock_remove,
        mock_transition,
        mock_validate_audit,
        mock_validate_sac,
    ):
        """Test that a valid submission transitions SAC to a disseminated state"""
        mock_validate_sac.return_value = ({}, {})
        mock_validate_audit.return_value = ({}, {})
        mock_disseminate.return_value = None
        response = self.client.post(self.url)

        mock_validate_sac.assert_called_once()
        mock_validate_audit.assert_called_once()
        mock_disseminate.assert_called_once()
        mock_transition.assert_called_with(
            response.wsgi_request,
            self.sac,
            audit=self.audit,
            transition_to=STATUS.DISSEMINATED,
        )
        mock_remove.assert_called_once()

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("audit:MySubmissions"))

    def test_get_access_denied_for_unauthorized_user(self):
        """Test that GET returns 403 if user is unauthorized"""
        self.client.logout()
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "home.html")
        self.assertTrue(response.context["session_expired"])

    @patch("audit.views.submissions.SingleAuditChecklist.validate_full")
    @patch("audit.models.Audit.validate")
    @patch("audit.views.submissions.sac_transition")
    @patch("audit.views.submissions.SingleAuditChecklist.disseminate")
    def test_post_validation_errors(
        self, mock_disseminate, mock_transition, mock_validate_audit, mock_validate_sac
    ):
        """Test that validation errors are displayed if submission is invalid"""
        mock_validate_audit.return_value = (["Error 1", "Error 2"], {})
        mock_validate_sac.return_value = (["Error 1", "Error 2"], {})
        self.sac.submission_status = STATUS.AUDITEE_CERTIFIED
        self.sac.save()

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "audit/cross-validation/cross-validation-results.html"
        )
        self.assertIn("errors", response.context)
        self.assertListEqual(response.context["errors"], ["Error 1", "Error 2"])

        mock_disseminate.assert_not_called()
        mock_transition.assert_not_called()

    @patch("audit.views.submissions.General.objects.get")
    @patch("audit.views.submissions.SingleAuditChecklist.validate_full")
    @patch("audit.models.Audit.validate")
    def test_post_transaction_error(
        self, mock_validate_audit, mock_validate_sac, mock_general_get
    ):
        """Test that a transaction error during a submission is handled properly"""
        self.sac.submission_status = STATUS.AUDITEE_CERTIFIED
        self.sac.save()

        awardsfile = "federal-awards--test0001test--simple-pass.json"
        self.audit.audit.update(
            **_load_json_audit_data(awardsfile, FORM_SECTIONS.FEDERAL_AWARDS)
        )
        self.audit.submission_status = STATUS.AUDITEE_CERTIFIED
        self.audit.save()

        mock_validate_audit.return_value = ({}, {})
        mock_validate_sac.return_value = ({}, {})
        mock_general_get.return_value = True

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("audit:MySubmissions"))

    def test_post_permission_denied_if_no_sac(self):
        """Test that POST returns 403 if SAC does not exist"""
        invalid_url = reverse("audit:Submission", kwargs={"report_id": "INVALID"})
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 403)

    def test_post_redirect(self):
        """
        The status should be "disseminated" after the post.
        The user should be redirected to the submissions table.
        """

        just_ueis = _just_uei_workbooks("TEST0001TEST")
        geninfofile = "general-information--test0001test--simple-pass.json"
        awardsfile = "federal-awards--test0001test--simple-pass.json"
        sequence = get_next_sequence_id(SAC_SEQUENCE_ID)

        sac_data = just_ueis | {
            "auditee_certification": _build_auditee_cert_dict(
                *fake_auditee_certification()
            ),
            "auditor_certification": _build_auditor_cert_dict(
                *fake_auditor_certification()
            ),
            "audit_information": _fake_audit_information(),
            "federal_awards": _load_json(AUDIT_JSON_FIXTURES / awardsfile),
            "general_information": _load_json(AUDIT_JSON_FIXTURES / geninfofile),
            "submission_status": STATUSES.IN_PROGRESS,  # Temporarily required for SAR creation below
        }
        sac_data["notes_to_sefa"]["NotesToSefa"]["accounting_policies"] = "Exhaustive"
        sac_data["notes_to_sefa"]["NotesToSefa"]["is_minimis_rate_used"] = "Y"
        sac_data["notes_to_sefa"]["NotesToSefa"]["rate_explained"] = "At great length"
        sac_data["id"] = sequence
        sac_data["report_id"] = _mock_gen_report_id(sequence)
        user, sac = _make_user_and_sac(**sac_data)

        required_statuses = (
            STATUSES.AUDITEE_CERTIFIED,
            STATUSES.AUDITOR_CERTIFIED,
            STATUSES.READY_FOR_CERTIFICATION,
            STATUSES.CERTIFIED,
        )

        for rs in required_statuses:
            sac.transition_name.append(rs)
            sac.transition_date.append(datetime.now(timezone.utc))

        audit_data = {
            "auditee_certification": _build_auditee_cert_dict(
                *fake_auditee_certification()
            ),
            "auditor_certification": _build_auditor_cert_dict(
                *fake_auditor_certification()
            ),
            "audit_information": _fake_audit_information(),
            "general_information": _load_json(AUDIT_JSON_FIXTURES / geninfofile),
            "notes_to_sefa": {
                "accounting_policies": "Exhaustive",
                "is_minimis_rate_used": "Y",
                "rate_explained": "At great length",
            },
            **_load_json_audit_data(awardsfile, FORM_SECTIONS.FEDERAL_AWARDS),
        }

        _, audit = _make_user_and_audit(sac.report_id, audit_data)

        baker.make(SingleAuditReportFile, sac=sac)
        baker.make(
            Access, user=user, sac=sac, audit=audit, role="certifying_auditee_contact"
        )

        sac.submission_status = STATUSES.AUDITEE_CERTIFIED
        sac.save()

        audit.submission_status = STATUSES.AUDITEE_CERTIFIED
        audit.save()

        response = _authed_post(
            Client(),
            user,
            "audit:Submission",
            kwargs={"report_id": sac.report_id},
            data={},
        )
        sac_after = SingleAuditChecklist.objects.get(report_id=sac.report_id)
        audit_after = Audit.objects.get(report_id=audit.report_id)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(sac_after.submission_status, STATUSES.DISSEMINATED)
        self.assertEqual(audit_after.submission_status, STATUSES.DISSEMINATED)


class SubmissionViewWithResubmissionTests(TestCase):
    """
    Testing for the final submission step when it is a resubmission.

    On resubmission, the view should:
        1. Disseminate the new SAC.
        2. Transition the previous SAC to RESUBMITTED.
        3. Redisseminate the previous SAC so that the status propagates through.
    """

    def setUp(self):
        """Set up a v1 disseminated SAC and an in-flight v2 SAC, with the appropriate resub metadata."""
        awardsfile = "federal-awards--test0001test--simple-pass.json"

        self.client = Client()
        self.user = baker.make(User)

        # v1, disseminated
        self.previous_audit = baker.make(
            Audit,
            version=0,
            audit={**_load_json_audit_data(awardsfile, FORM_SECTIONS.FEDERAL_AWARDS)},
            submission_status=STATUS.DISSEMINATED,
        )
        self.previous_sac = baker.make(
            SingleAuditChecklist,
            submission_status=STATUS.DISSEMINATED,
            report_id=self.previous_audit.report_id,
        )

        # v2, certified, points at v1
        self.audit = baker.make(
            Audit,
            version=0,
            audit={**_load_json_audit_data(awardsfile, FORM_SECTIONS.FEDERAL_AWARDS)},
            submission_status=STATUS.AUDITEE_CERTIFIED,
        )
        self.sac = baker.make(
            SingleAuditChecklist,
            submission_status=STATUS.AUDITEE_CERTIFIED,
            report_id=self.audit.report_id,
            resubmission_meta={
                "previous_report_id": self.previous_sac.report_id,
                "previous_row_id": self.previous_sac.id,
                "resubmission_status": RESUBMISSION_STATUS.MOST_RECENT,
                "version": 2,
            },
        )

        self.url = reverse(
            "audit:Submission", kwargs={"report_id": self.audit.report_id}
        )
        self.client.force_login(self.user)
        baker.make(
            "audit.Access",
            sac=self.sac,
            user=self.user,
            role="certifying_auditee_contact",
        )

    @patch("audit.models.SingleAuditChecklist.redisseminate")
    @patch("audit.models.SingleAuditChecklist.validate_full")
    @patch("audit.models.Audit.validate")
    @patch("audit.views.submissions.remove_workbook_artifacts")
    @patch("audit.views.submissions.SingleAuditChecklist.disseminate")
    def test_resubmission_deprecates_previous_and_disseminates_new(
        self,
        mock_disseminate,
        mock_remove,
        mock_validate_audit,
        mock_validate_sac,
        mock_redisseminate,
    ):
        """
        A successful resubmission should disseminate the new SAC, transition
        the previous SAC to RESUBMITTED, mark its resubmission_meta as
        DEPRECATED (pointing at the new report_id), and redisseminate it.
        """
        mock_validate_sac.return_value = ({}, {})
        mock_validate_audit.return_value = ({}, {})
        mock_disseminate.return_value = None

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("audit:MySubmissions"))

        # The v2 SAC should have been disseminated, and the v1 should have been redisseminated.
        mock_disseminate.assert_called_once()
        mock_redisseminate.assert_called_once()

        # The v1 SAC should have been transitioned to RESUBMITTED, and
        # its resubmission_meta should reflect the deprecation.
        previous_sac_after = SingleAuditChecklist.objects.get(
            report_id=self.previous_sac.report_id
        )
        self.assertEqual(previous_sac_after.submission_status, STATUS.RESUBMITTED)
        self.assertEqual(
            previous_sac_after.resubmission_meta["resubmission_status"],
            RESUBMISSION_STATUS.DEPRECATED,
        )
        self.assertEqual(
            previous_sac_after.resubmission_meta["next_report_id"], self.sac.report_id
        )

        # The v2 SAC should be disseminated.
        new_after = SingleAuditChecklist.objects.get(report_id=self.sac.report_id)
        self.assertEqual(new_after.submission_status, STATUS.DISSEMINATED)

        mock_remove.assert_called_once()

    @patch("audit.models.SingleAuditChecklist.redisseminate")
    @patch("audit.models.SingleAuditChecklist.validate_full")
    @patch("audit.models.Audit.validate")
    @patch("audit.views.submissions.SingleAuditChecklist.disseminate")
    def test_resubmission_validation_errors_prevent_dissemination(
        self,
        mock_disseminate,
        mock_validate_audit,
        mock_validate_sac,
        mock_redisseminate,
    ):
        """
        If the v2 SAC fails full validation, neither the v2 nor v1 should be disseminated, and
        the v1 should remain untouched.
        """
        mock_validate_audit.return_value = ({}, {})
        mock_validate_sac.return_value = (["Error 1"], {})

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "audit/cross-validation/cross-validation-results.html"
        )

        mock_disseminate.assert_not_called()
        mock_redisseminate.assert_not_called()

        previous_sac_after = SingleAuditChecklist.objects.get(
            report_id=self.previous_sac.report_id
        )
        self.assertEqual(previous_sac_after.submission_status, STATUS.DISSEMINATED)
        self.assertNotIn(
            "resubmission_status", previous_sac_after.resubmission_meta or {}
        )

        new_after = SingleAuditChecklist.objects.get(report_id=self.sac.report_id)
        self.assertEqual(new_after.submission_status, STATUS.AUDITEE_CERTIFIED)

    @patch("audit.models.SingleAuditChecklist.redisseminate")
    @patch("audit.models.SingleAuditChecklist.validate_full")
    @patch("audit.models.Audit.validate")
    @patch("audit.views.submissions.remove_workbook_artifacts")
    @patch("audit.views.submissions.SingleAuditChecklist.disseminate")
    def test_dissemination_failure_skips_new_sac_finalization_but_still_deprecates_previous(
        self,
        mock_disseminate,
        mock_remove,
        mock_validate_audit,
        mock_validate_sac,
        mock_redisseminate,
    ):
        """
        If dissemination of v2 fails, then v2 should not be transitioned to
        DISSEMINATED and workbook artifacts should not be removed. v1 is still deprecated.
        """
        mock_validate_sac.return_value = ({}, {})
        mock_validate_audit.return_value = ({}, {})
        mock_disseminate.return_value = {"errors": ["the sac errs on validation"]}

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("audit:MySubmissions"))

        mock_redisseminate.assert_called_once()
        mock_remove.assert_not_called()

        previous_sac_after = SingleAuditChecklist.objects.get(
            report_id=self.previous_sac.report_id
        )
        self.assertEqual(previous_sac_after.submission_status, STATUS.RESUBMITTED)

        sac_after = SingleAuditChecklist.objects.get(report_id=self.sac.report_id)
        self.assertNotEqual(sac_after.submission_status, STATUS.DISSEMINATED)
