import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from unittest.mock import patch

from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from model_bakery import baker

from openpyxl import load_workbook
from openpyxl.cell import Cell

from .fixtures.excel import (
    ADDITIONAL_UEIS_TEMPLATE,
    ADDITIONAL_EINS_TEMPLATE,
    FEDERAL_AWARDS_TEMPLATE,
    CORRECTIVE_ACTION_PLAN_TEMPLATE,
    FINDINGS_TEXT_TEMPLATE,
    FINDINGS_UNIFORM_GUIDANCE_TEMPLATE,
    SECONDARY_AUDITORS_TEMPLATE,
    NOTES_TO_SEFA_TEMPLATE,
    CORRECTIVE_ACTION_PLAN_ENTRY_FIXTURES,
    FINDINGS_TEXT_ENTRY_FIXTURES,
    FINDINGS_UNIFORM_GUIDANCE_ENTRY_FIXTURES,
    FEDERAL_AWARDS_ENTRY_FIXTURES,
    ADDITIONAL_UEIS_ENTRY_FIXTURES,
    ADDITIONAL_EINS_ENTRY_FIXTURES,
    SECONDARY_AUDITORS_ENTRY_FIXTURES,
    NOTES_TO_SEFA_ENTRY_FIXTURES,
    FORM_SECTIONS,
)
from .fixtures.single_audit_checklist import (
    fake_auditor_certification,
    fake_auditee_certification,
)
from .models import Access, SingleAuditChecklist, SingleAuditReportFile
from .views import MySubmissions

User = get_user_model()

SUBMISSIONS_PATH = reverse("audit:MySubmissions")
EDIT_PATH = "audit:EditSubmission"
ACCESS_AND_SUBMISSION_PATH = reverse("report_submission:accessandsubmission")

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
    "certifying_auditee_contact_fullname": "Fuller A. Namesmith",
    "certifying_auditee_contact_email": "a@a.com",
    "certifying_auditor_contact_fullname": "Fuller B. Namesmith",
    "certifying_auditor_contact_email": "b@b.com",
    "auditee_contacts_fullname": ["Fuller C. Namesmith"],
    "auditee_contacts_email": ["c@c.com"],
    "auditor_contacts_fullname": ["Fuller D. Namesmith"],
    "auditor_contacts_email": ["d@d.com"],
}

AUDIT_JSON_FIXTURES = Path(__file__).parent / "fixtures" / "json"


# Mocking the user login and file scan functions
def _mock_login_and_scan(client, mock_scan_file):
    """Helper function to mock the login and file scan functions"""
    user, sac = _make_user_and_sac()

    baker.make(Access, user=user, sac=sac)

    client.force_login(user)

    # mock the call to the external AV service
    mock_scan_file.return_value = MockHttpResponse(200, "clean!")

    return sac


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
    user = baker.make(User)
    sac = baker.make(SingleAuditChecklist, **kwargs)
    return user, sac


def _load_json(target):
    """Given a str or Path, load JSON from that target."""
    raw = Path(target).read_text(encoding="utf-8")
    return json.loads(raw)


class MySubmissionsViewTests(TestCase):
    def setUp(self):
        self.user = baker.make(User)
        self.user2 = baker.make(User)

        self.client = Client()

    def test_redirect_if_not_logged_in(self):
        result = self.client.get(SUBMISSIONS_PATH)
        self.assertAlmostEquals(result.status_code, 302)

    def test_no_submissions_returns_empty_list(self):
        self.client.force_login(user=self.user)
        data = MySubmissions.fetch_my_submissions(self.user)
        self.assertEquals(len(data), 0)

    def test_user_with_submissions_should_return_expected_data_columns(self):
        self.client.force_login(user=self.user)
        self.user.profile.entry_form_data = (
            VALID_ELIGIBILITY_DATA | VALID_AUDITEE_INFO_DATA
        )
        self.user.profile.save()
        self.client.post(
            ACCESS_AND_SUBMISSION_PATH, VALID_ACCESS_AND_SUBMISSION_DATA, format="json"
        )
        data = MySubmissions.fetch_my_submissions(self.user)
        self.assertGreater(len(data), 0)

        keys = data[0].keys()
        self.assertTrue("report_id" in keys)
        self.assertTrue("submission_status" in keys)
        self.assertTrue("auditee_uei" in keys)
        self.assertTrue("auditee_name" in keys)
        self.assertTrue("fiscal_year_end_date" in keys)

    def test_user_with_no_submissions_should_return_no_data(self):
        self.client.force_login(user=self.user)
        self.user.profile.entry_form_data = (
            VALID_ELIGIBILITY_DATA | VALID_AUDITEE_INFO_DATA
        )
        self.user.profile.save()
        self.client.post(
            ACCESS_AND_SUBMISSION_PATH, VALID_ACCESS_AND_SUBMISSION_DATA, format="json"
        )
        data = MySubmissions.fetch_my_submissions(self.user2)
        self.assertEquals(len(data), 0)


class EditSubmissionViewTests(TestCase):
    def test_redirect_if_not_logged_in(self):
        result = self.client.get(reverse(EDIT_PATH, args=["SOME_REPORT_ID"]))
        self.assertAlmostEquals(result.status_code, 302)


class SubmissionViewTests(TestCase):
    """
    Testing for the final step: submitting.
    """

    def test_post_redirect(self):
        """
        The status should be "submitted" after the post.
        The user should be redirected to the submissions table.
        """
        user = baker.make(User)
        sac = baker.make(
            SingleAuditChecklist,
            submission_status=SingleAuditChecklist.STATUS.AUDITEE_CERTIFIED,
        )
        baker.make(Access, user=user, sac=sac, role="certifying_auditee_contact")
        response = _authed_post(
            Client(),
            user,
            "audit:Submission",
            kwargs={"report_id": sac.report_id},
            data={},
        )
        sac_after = SingleAuditChecklist.objects.get(report_id=sac.report_id)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(sac_after.submission_status, sac_after.STATUS.SUBMITTED)


class SubmissionStatusTests(TestCase):
    """
    Tests the expected order of progression for submission_status.

    Does not yet test that only users with the appropriate permissions can
    access the relevant pages.

    Does not test attempts at incorrect progressions, as these are handled by
    tests in test_models.py.
    """

    def setUp(self):
        self.user = baker.make(User)
        self.client = Client()

    def test_ready_for_certification(self):
        """
        Test that the submitting user can mark the submission as ready for certification
        """
        self.client.force_login(user=self.user)
        self.user.profile.entry_form_data = (
            VALID_ELIGIBILITY_DATA | VALID_AUDITEE_INFO_DATA
        )
        self.user.profile.save()
        self.client.post(
            ACCESS_AND_SUBMISSION_PATH, VALID_ACCESS_AND_SUBMISSION_DATA, format="json"
        )
        data = MySubmissions.fetch_my_submissions(self.user)
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]["submission_status"], "in_progress")
        report_id = data[0]["report_id"]

        filename = "general-information--test0001test--simple-pass.json"
        info = _load_json(AUDIT_JSON_FIXTURES / filename)
        # Update the SAC so that it will pass overall validation:
        sac = SingleAuditChecklist.objects.get(report_id=report_id)
        sac.general_information = info
        sac.audit_information = {"stuff": "whatever"}
        sac.federal_awards = {"FederalAwards": {"federal_awards": []}}
        sac.corrective_action_plan = {
            "CorrectiveActionPlan": {"auditee_uei": "TEST0001TEST"}
        }
        sac.findings_text = {"FindingsText": {"auditee_uei": "TEST0001TEST"}}
        sac.findings_uniform_guidance = {
            "FindingsUniformGuidance": {"auditee_uei": "TEST0001TEST"}
        }
        sac.notes_to_sefa = {"NotesToSefa": {"auditee_uei": "TEST0001TEST"}}
        baker.make(SingleAuditReportFile, sac=sac)
        sac.save()

        self.client.post(f"/audit/ready-for-certification/{report_id}", data={})
        data = MySubmissions.fetch_my_submissions(self.user)

        self.assertEqual(data[0]["submission_status"], "ready_for_certification")

    def test_auditor_certification(self):
        """
        Test that certifying auditor contacts can provide auditor certification
        """
        data_step_1, data_step_2 = fake_auditor_certification()

        user, sac = _make_user_and_sac(submission_status="ready_for_certification")
        baker.make(Access, sac=sac, user=user, role="certifying_auditor_contact")

        kwargs = {"report_id": sac.report_id}
        _authed_post(
            self.client,
            user,
            "audit:AuditorCertification",
            kwargs=kwargs,
            data=data_step_1,
        )
        _authed_post(
            self.client,
            user,
            "audit:AuditorCertificationConfirm",
            kwargs=kwargs,
            data=data_step_2,
        )

        updated_sac = SingleAuditChecklist.objects.get(report_id=sac.report_id)

        self.assertEqual(updated_sac.submission_status, "auditor_certified")

    def test_auditee_certification(self):
        """
        Test that certifying auditee contacts can provide auditee certification
        """
        data_step_1, data_step_2 = fake_auditee_certification()

        user, sac = _make_user_and_sac(submission_status="auditor_certified")
        baker.make(Access, sac=sac, user=user, role="certifying_auditee_contact")

        kwargs = {"report_id": sac.report_id}
        _authed_post(
            self.client,
            user,
            "audit:AuditeeCertification",
            kwargs=kwargs,
            data=data_step_1,
        )
        _authed_post(
            self.client,
            user,
            "audit:AuditeeCertificationConfirm",
            kwargs=kwargs,
            data=data_step_2,
        )

        updated_sac = SingleAuditChecklist.objects.get(report_id=sac.report_id)

        self.assertEqual(updated_sac.submission_status, "auditee_certified")

    def test_submission(self):
        """
        Test that certifying auditee contacts can perform submission
        """
        user, sac = _make_user_and_sac(submission_status="auditee_certified")
        baker.make(Access, sac=sac, user=user, role="certifying_auditee_contact")

        kwargs = {"report_id": sac.report_id}
        _authed_post(self.client, user, "audit:Submission", kwargs=kwargs)

        updated_sac = SingleAuditChecklist.objects.get(report_id=sac.report_id)

        self.assertEqual(updated_sac.submission_status, "submitted")


class MockHttpResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text


def _set_by_name(workbook, name, value, row_offset=0):
    definition = workbook.defined_names[name]

    sheet_title, cell_coord = next(definition.destinations)

    sheet = workbook[sheet_title]
    cell_range = sheet[cell_coord]

    if isinstance(cell_range, Cell):
        cell_range.value = value
    else:
        cell_range[row_offset][0].value = value


def _add_entry(workbook, row_offset, entry):
    for key, value in entry.items():
        _set_by_name(workbook, key, value, row_offset)


class ExcelFileHandlerViewTests(TestCase):
    GOOD_UEI = "AAA123456BBB"

    def test_login_required(self):
        """When an unauthenticated request is made"""

        for form_section in FORM_SECTIONS:
            response = self.client.post(
                reverse(
                    f"audit:{form_section}",
                    kwargs={"report_id": "12345", "form_section": form_section},
                )
            )

            self.assertEqual(response.status_code, 403)

    def test_bad_report_id_returns_403(self):
        """When a request is made for a malformed or nonexistent report_id, a 403 error should be returned"""
        user = baker.make(User)

        self.client.force_login(user)

        for form_section in FORM_SECTIONS:
            response = self.client.post(
                reverse(
                    f"audit:{form_section}",
                    kwargs={
                        "report_id": "this is not a report id",
                        "form_section": form_section,
                    },
                )
            )

            self.assertEqual(response.status_code, 403)

    def test_inaccessible_audit_returns_403(self):
        """When a request is made for an audit that is inaccessible for this user, a 403 error should be returned"""
        user, sac = _make_user_and_sac()

        self.client.force_login(user)
        for form_section in FORM_SECTIONS:
            response = self.client.post(
                reverse(
                    f"audit:{form_section}",
                    kwargs={"report_id": sac.report_id, "form_section": form_section},
                )
            )

            self.assertEqual(response.status_code, 403)

    def test_no_file_attached_returns_400(self):
        """When a request is made with no file attached, a 400 error should be returned"""
        user, sac = _make_user_and_sac()
        baker.make(Access, user=user, sac=sac)

        self.client.force_login(user)

        for form_section in FORM_SECTIONS:
            response = self.client.post(
                reverse(
                    f"audit:{form_section}",
                    kwargs={"report_id": sac.report_id, "form_section": form_section},
                )
            )

            self.assertEqual(response.status_code, 400)

    def test_invalid_file_upload_returns_400(self):
        """When an invalid Excel file is uploaded, a 400 error should be returned"""
        user, sac = _make_user_and_sac()
        baker.make(Access, user=user, sac=sac)

        self.client.force_login(user)

        file = SimpleUploadedFile("not-excel.txt", b"asdf", "text/plain")

        for form_section in FORM_SECTIONS:
            response = self.client.post(
                reverse(
                    f"audit:{form_section}",
                    kwargs={"report_id": sac.report_id, "form_section": form_section},
                ),
                data={"FILES": file},
            )

            self.assertEqual(response.status_code, 400)

    @patch("audit.validators._scan_file")
    def test_valid_file_upload_for_federal_awards(self, mock_scan_file):
        """When a valid Excel file is uploaded, the file should be stored and the SingleAuditChecklist should be updated to include the uploaded Federal Awards data"""

        sac = _mock_login_and_scan(self.client, mock_scan_file)
        test_data = json.loads(
            FEDERAL_AWARDS_ENTRY_FIXTURES.read_text(encoding="utf-8")
        )

        # add valid data to the workbook
        workbook = load_workbook(FEDERAL_AWARDS_TEMPLATE, data_only=True)
        _set_by_name(workbook, "auditee_uei", ExcelFileHandlerViewTests.GOOD_UEI)
        _set_by_name(workbook, "section_name", FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED)
        _add_entry(workbook, 0, test_data[0])

        with NamedTemporaryFile(suffix=".xlsx") as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)

            with open(tmp.name, "rb") as excel_file:
                response = self.client.post(
                    reverse(
                        f"audit:{FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED}",
                        kwargs={
                            "report_id": sac.report_id,
                            "form_section": FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED,
                        },
                    ),
                    data={"FILES": excel_file},
                )

                self.assertEqual(response.status_code, 302)

                updated_sac = SingleAuditChecklist.objects.get(pk=sac.id)

                self.assertEqual(
                    updated_sac.federal_awards["FederalAwards"]["auditee_uei"],
                    ExcelFileHandlerViewTests.GOOD_UEI,
                )
                self.assertEqual(
                    len(updated_sac.federal_awards["FederalAwards"]["federal_awards"]),
                    1,
                )

                federal_awards_entry = updated_sac.federal_awards["FederalAwards"][
                    "federal_awards"
                ][0]

                self.assertEqual(
                    federal_awards_entry["cluster"]["cluster_name"],
                    test_data[0]["cluster_name"],
                )
                self.assertEqual(
                    federal_awards_entry["direct_or_indirect_award"]["is_direct"],
                    test_data[0]["is_direct"],
                )
                self.assertEqual(
                    federal_awards_entry["program"]["is_major"],
                    test_data[0]["is_major"],
                )
                self.assertEqual(
                    federal_awards_entry["program"]["federal_agency_prefix"],
                    test_data[0]["federal_agency_prefix"],
                )
                self.assertEqual(
                    federal_awards_entry["program"]["three_digit_extension"],
                    test_data[0]["three_digit_extension"],
                )
                self.assertEqual(
                    federal_awards_entry["program"]["amount_expended"],
                    test_data[0]["amount_expended"],
                )
                self.assertEqual(
                    federal_awards_entry["program"]["program_name"],
                    test_data[0]["program_name"],
                )
                self.assertEqual(
                    federal_awards_entry["loan_or_loan_guarantee"]["is_guaranteed"],
                    test_data[0]["is_guaranteed"],
                )
                self.assertEqual(
                    federal_awards_entry["program"]["number_of_audit_findings"],
                    test_data[0]["number_of_audit_findings"],
                )
                self.assertEqual(
                    federal_awards_entry["program"]["audit_report_type"],
                    test_data[0]["audit_report_type"],
                )
                self.assertEqual(
                    federal_awards_entry["loan_or_loan_guarantee"][
                        "loan_balance_at_audit_period_end"
                    ],
                    test_data[0]["loan_balance_at_audit_period_end"],
                )
                self.assertEqual(
                    federal_awards_entry["subrecipients"]["is_passed"],
                    test_data[0]["is_passed"],
                )
                self.assertEqual(
                    federal_awards_entry["subrecipients"]["subrecipient_amount"],
                    test_data[0]["subrecipient_amount"],
                )
                self.assertEqual(
                    federal_awards_entry["direct_or_indirect_award"]["entities"],
                    [
                        {
                            "passthrough_name": "A",
                            "passthrough_identifying_number": "1",
                        },
                        {
                            "passthrough_name": "B",
                            "passthrough_identifying_number": "2",
                        },
                    ],
                )

    @patch("audit.validators._scan_file")
    def test_valid_file_upload_for_corrective_action_plan(self, mock_scan_file):
        """When a valid Excel file is uploaded, the file should be stored and the SingleAuditChecklist should be updated to include the uploaded Corrective Action Plan data"""

        test_uei = "AAA12345678X"
        sac = _mock_login_and_scan(self.client, mock_scan_file)
        test_data = json.loads(
            CORRECTIVE_ACTION_PLAN_ENTRY_FIXTURES.read_text(encoding="utf-8")
        )

        # add valid data to the workbook
        workbook = load_workbook(CORRECTIVE_ACTION_PLAN_TEMPLATE, data_only=True)
        _set_by_name(workbook, "auditee_uei", test_uei)
        _set_by_name(workbook, "section_name", FORM_SECTIONS.CORRECTIVE_ACTION_PLAN)

        _add_entry(workbook, 0, test_data[0])

        with NamedTemporaryFile(suffix=".xlsx") as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)

            with open(tmp.name, "rb") as excel_file:
                response = self.client.post(
                    reverse(
                        f"audit:{FORM_SECTIONS.CORRECTIVE_ACTION_PLAN}",
                        kwargs={
                            "report_id": sac.report_id,
                            "form_section": FORM_SECTIONS.CORRECTIVE_ACTION_PLAN,
                        },
                    ),
                    data={"FILES": excel_file},
                )

                self.assertEqual(response.status_code, 302)

                updated_sac = SingleAuditChecklist.objects.get(pk=sac.id)

                self.assertEqual(
                    updated_sac.corrective_action_plan["CorrectiveActionPlan"][
                        "auditee_uei"
                    ],
                    test_uei,
                )

                self.assertEqual(
                    len(
                        updated_sac.corrective_action_plan["CorrectiveActionPlan"][
                            "corrective_action_plan_entries"
                        ]
                    ),
                    1,
                )

                corrective_action_plan_entry = updated_sac.corrective_action_plan[
                    "CorrectiveActionPlan"
                ]["corrective_action_plan_entries"][0]

                self.assertEqual(
                    corrective_action_plan_entry["planned_action"],
                    test_data[0]["planned_action"],
                )
                self.assertEqual(
                    corrective_action_plan_entry["reference_number"],
                    test_data[0]["reference_number"],
                )

    @patch("audit.validators._scan_file")
    def test_valid_file_upload_for_findings_uniform_guidance(self, mock_scan_file):
        """When a valid Excel file is uploaded, the file should be stored and the SingleAuditChecklist should be updated to include the uploaded Findings Uniform Guidance data"""

        sac = _mock_login_and_scan(self.client, mock_scan_file)
        test_data = json.loads(
            FINDINGS_UNIFORM_GUIDANCE_ENTRY_FIXTURES.read_text(encoding="utf-8")
        )

        # add valid data to the workbook
        workbook = load_workbook(FINDINGS_UNIFORM_GUIDANCE_TEMPLATE, data_only=True)
        _set_by_name(workbook, "auditee_uei", ExcelFileHandlerViewTests.GOOD_UEI)
        _set_by_name(workbook, "section_name", FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE)
        _add_entry(workbook, 0, test_data[0])

        with NamedTemporaryFile(suffix=".xlsx") as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)

            with open(tmp.name, "rb") as excel_file:
                response = self.client.post(
                    reverse(
                        f"audit:{FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE}",
                        kwargs={
                            "report_id": sac.report_id,
                            "form_section": FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE,
                        },
                    ),
                    data={"FILES": excel_file},
                )

                self.assertEqual(response.status_code, 302)

                updated_sac = SingleAuditChecklist.objects.get(pk=sac.id)

                self.assertEqual(
                    updated_sac.findings_uniform_guidance["FindingsUniformGuidance"][
                        "auditee_uei"
                    ],
                    ExcelFileHandlerViewTests.GOOD_UEI,
                )

                self.assertEqual(
                    len(
                        updated_sac.findings_uniform_guidance[
                            "FindingsUniformGuidance"
                        ]["findings_uniform_guidance_entries"]
                    ),
                    1,
                )

                findings_entries = updated_sac.findings_uniform_guidance[
                    "FindingsUniformGuidance"
                ]["findings_uniform_guidance_entries"][0]

                self.assertEqual(
                    findings_entries["program"]["award_reference"],
                    test_data[0]["award_reference"],
                )
                self.assertEqual(
                    findings_entries["program"]["compliance_requirement"],
                    test_data[0]["compliance_requirement"],
                )
                self.assertEqual(
                    findings_entries["findings"]["repeat_prior_reference"],
                    test_data[0]["repeat_prior_reference"],
                )
                self.assertEqual(
                    findings_entries["findings"]["reference_number"],
                    test_data[0]["reference_number"],
                )
                self.assertEqual(
                    findings_entries["modified_opinion"],
                    test_data[0]["modified_opinion"],
                )

    @patch("audit.validators._scan_file")
    def test_valid_file_upload_for_findings_text(self, mock_scan_file):
        """When a valid Excel file is uploaded, the file should be stored and the SingleAuditChecklist should be updated to include the uploaded Findings Text data"""

        sac = _mock_login_and_scan(self.client, mock_scan_file)
        test_data = json.loads(FINDINGS_TEXT_ENTRY_FIXTURES.read_text(encoding="utf-8"))

        # add valid data to the workbook
        workbook = load_workbook(FINDINGS_TEXT_TEMPLATE, data_only=True)
        _set_by_name(workbook, "auditee_uei", ExcelFileHandlerViewTests.GOOD_UEI)
        _set_by_name(workbook, "section_name", FORM_SECTIONS.FINDINGS_TEXT)
        _add_entry(workbook, 0, test_data[0])

        with NamedTemporaryFile(suffix=".xlsx") as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)

            with open(tmp.name, "rb") as excel_file:
                response = self.client.post(
                    reverse(
                        f"audit:{FORM_SECTIONS.FINDINGS_TEXT}",
                        kwargs={
                            "report_id": sac.report_id,
                            "form_section": FORM_SECTIONS.FINDINGS_TEXT,
                        },
                    ),
                    data={"FILES": excel_file},
                )

                self.assertEqual(response.status_code, 302)

                updated_sac = SingleAuditChecklist.objects.get(pk=sac.id)

                self.assertEqual(
                    updated_sac.findings_text["FindingsText"]["auditee_uei"],
                    ExcelFileHandlerViewTests.GOOD_UEI,
                )

                self.assertEqual(
                    len(
                        updated_sac.findings_text["FindingsText"][
                            "findings_text_entries"
                        ]
                    ),
                    1,
                )

                findings_entries = updated_sac.findings_text["FindingsText"][
                    "findings_text_entries"
                ][0]

                self.assertEqual(
                    findings_entries["contains_chart_or_table"],
                    test_data[0]["contains_chart_or_table"],
                )
                self.assertEqual(
                    findings_entries["text_of_finding"],
                    test_data[0]["text_of_finding"],
                )
                self.assertEqual(
                    findings_entries["reference_number"],
                    test_data[0]["reference_number"],
                )

    @patch("audit.validators._scan_file")
    def test_valid_file_upload_for_secondary_auditors(self, mock_scan_file):
        """When a valid Excel file is uploaded, the file should be stored and the SingleAuditChecklist should be updated to include the uploaded secondary auditors data"""

        sac = _mock_login_and_scan(self.client, mock_scan_file)
        test_data = json.loads(
            SECONDARY_AUDITORS_ENTRY_FIXTURES.read_text(encoding="utf-8")
        )

        # add valid data to the workbook
        workbook = load_workbook(SECONDARY_AUDITORS_TEMPLATE, data_only=True)
        _set_by_name(workbook, "auditee_uei", ExcelFileHandlerViewTests.GOOD_UEI)
        _set_by_name(workbook, "section_name", FORM_SECTIONS.SECONDARY_AUDITORS)
        _add_entry(workbook, 0, test_data[0])

        with NamedTemporaryFile(suffix=".xlsx") as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)

            with open(tmp.name, "rb") as excel_file:
                response = self.client.post(
                    reverse(
                        f"audit:{FORM_SECTIONS.SECONDARY_AUDITORS}",
                        kwargs={
                            "report_id": sac.report_id,
                            "form_section": FORM_SECTIONS.SECONDARY_AUDITORS,
                        },
                    ),
                    data={"FILES": excel_file},
                )

                self.assertEqual(response.status_code, 302)

                updated_sac = SingleAuditChecklist.objects.get(pk=sac.id)

                self.assertEqual(
                    updated_sac.secondary_auditors["SecondaryAuditors"]["auditee_uei"],
                    ExcelFileHandlerViewTests.GOOD_UEI,
                )

                self.assertEqual(
                    len(
                        updated_sac.secondary_auditors["SecondaryAuditors"][
                            "secondary_auditors_entries"
                        ]
                    ),
                    1,
                )

                secondary_auditors_entries = updated_sac.secondary_auditors[
                    "SecondaryAuditors"
                ]["secondary_auditors_entries"][0]

                self.assertEqual(
                    secondary_auditors_entries["secondary_auditor_name"],
                    test_data[0]["secondary_auditor_name"],
                )
                self.assertEqual(
                    secondary_auditors_entries["secondary_auditor_ein"],
                    test_data[0]["secondary_auditor_ein"],
                )
                self.assertEqual(
                    secondary_auditors_entries["secondary_auditor_address_street"],
                    test_data[0]["secondary_auditor_address_street"],
                )
                self.assertEqual(
                    secondary_auditors_entries["secondary_auditor_address_city"],
                    test_data[0]["secondary_auditor_address_city"],
                )
                self.assertEqual(
                    secondary_auditors_entries["secondary_auditor_address_state"],
                    test_data[0]["secondary_auditor_address_state"],
                )
                self.assertEqual(
                    secondary_auditors_entries["secondary_auditor_address_zipcode"],
                    test_data[0]["secondary_auditor_address_zipcode"],
                )
                self.assertEqual(
                    secondary_auditors_entries["secondary_auditor_contact_name"],
                    test_data[0]["secondary_auditor_contact_name"],
                )
                self.assertEqual(
                    secondary_auditors_entries["secondary_auditor_contact_title"],
                    test_data[0]["secondary_auditor_contact_title"],
                )
                self.assertEqual(
                    secondary_auditors_entries["secondary_auditor_contact_phone"],
                    test_data[0]["secondary_auditor_contact_phone"],
                )
                self.assertEqual(
                    secondary_auditors_entries["secondary_auditor_contact_email"],
                    test_data[0]["secondary_auditor_contact_email"],
                )


class SingleAuditReportFileHandlerViewTests(TestCase):
    def test_login_required(self):
        """When an unauthenticated request is made"""

        response = self.client.post(
            reverse(
                "audit:SingleAuditReport",
                kwargs={"report_id": "12345"},
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_bad_report_id_returns_403(self):
        """When a request is made for a malformed or nonexistent report_id, a 403 error should be returned"""
        user = baker.make(User)

        self.client.force_login(user)

        response = self.client.post(
            reverse(
                "audit:SingleAuditReport",
                kwargs={
                    "report_id": "this is not a report id",
                },
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_inaccessible_audit_returns_403(self):
        """When a request is made for an audit that is inaccessible for this user, a 403 error should be returned"""
        user, sac = _make_user_and_sac()

        self.client.force_login(user)
        response = self.client.post(
            reverse(
                "audit:SingleAuditReport",
                kwargs={"report_id": sac.report_id},
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_no_file_attached_returns_400(self):
        """When a request is made with no file attached, a 400 error should be returned"""
        user, sac = _make_user_and_sac()
        baker.make(Access, user=user, sac=sac)

        self.client.force_login(user)

        response = self.client.post(
            reverse(
                "audit:SingleAuditReport",
                kwargs={"report_id": sac.report_id},
            )
        )

        self.assertEqual(response.status_code, 400)

    @patch("audit.validators._scan_file")
    def test_valid_file_upload(self, mock_scan_file):
        sac = _mock_login_and_scan(self.client, mock_scan_file)

        with open("audit/fixtures/basic.pdf", "rb") as pdf_file:
            response = self.client.post(
                reverse(
                    "audit:SingleAuditReport",
                    kwargs={
                        "report_id": sac.report_id,
                    },
                ),
                data={"FILES": pdf_file},
            )

            self.assertEqual(response.status_code, 302)

    @patch("audit.validators._scan_file")
    def test_valid_file_upload_for_additional_ueis(self, mock_scan_file):
        """When a valid Excel file is uploaded, the file should be stored and the SingleAuditChecklist should be updated to include the uploaded Additional UEIs data"""

        sac = _mock_login_and_scan(self.client, mock_scan_file)
        test_data = json.loads(
            ADDITIONAL_UEIS_ENTRY_FIXTURES.read_text(encoding="utf-8")
        )

        # add valid data to the workbook
        workbook = load_workbook(ADDITIONAL_UEIS_TEMPLATE, data_only=True)
        _set_by_name(workbook, "auditee_uei", ExcelFileHandlerViewTests.GOOD_UEI)
        _set_by_name(workbook, "section_name", FORM_SECTIONS.ADDITIONAL_UEIS)
        _add_entry(workbook, 0, test_data[0])

        with NamedTemporaryFile(suffix=".xlsx") as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)

            with open(tmp.name, "rb") as excel_file:
                response = self.client.post(
                    reverse(
                        f"audit:{FORM_SECTIONS.ADDITIONAL_UEIS}",
                        kwargs={
                            "report_id": sac.report_id,
                            "form_section": FORM_SECTIONS.ADDITIONAL_UEIS,
                        },
                    ),
                    data={"FILES": excel_file},
                )

                self.assertEqual(response.status_code, 302)

                updated_sac = SingleAuditChecklist.objects.get(pk=sac.id)

                self.assertEqual(
                    updated_sac.additional_ueis["AdditionalUEIs"]["auditee_uei"],
                    ExcelFileHandlerViewTests.GOOD_UEI,
                )

                self.assertEqual(
                    len(
                        updated_sac.additional_ueis["AdditionalUEIs"][
                            "additional_ueis_entries"
                        ]
                    ),
                    1,
                )

                additional_ueis_entries = updated_sac.additional_ueis["AdditionalUEIs"][
                    "additional_ueis_entries"
                ][0]

                self.assertEqual(
                    additional_ueis_entries["additional_uei"],
                    test_data[0]["additional_uei"],
                )

    @patch("audit.validators._scan_file")
    def test_valid_file_upload_for_additional_eins(self, mock_scan_file):
        """When a valid Excel file is uploaded, the file should be stored and the SingleAuditChecklist should be updated to include the uploaded Additional EINs data"""

        sac = _mock_login_and_scan(self.client, mock_scan_file)
        test_data = json.loads(
            ADDITIONAL_EINS_ENTRY_FIXTURES.read_text(encoding="utf-8")
        )

        # add valid data to the workbook
        workbook = load_workbook(ADDITIONAL_EINS_TEMPLATE, data_only=True)
        _set_by_name(workbook, "auditee_uei", ExcelFileHandlerViewTests.GOOD_UEI)
        _set_by_name(workbook, "section_name", FORM_SECTIONS.ADDITIONAL_EINS)
        _add_entry(workbook, 0, test_data[0])

        with NamedTemporaryFile(suffix=".xlsx") as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)

            with open(tmp.name, "rb") as excel_file:
                response = self.client.post(
                    reverse(
                        f"audit:{FORM_SECTIONS.ADDITIONAL_EINS}",
                        kwargs={
                            "report_id": sac.report_id,
                            "form_section": FORM_SECTIONS.ADDITIONAL_EINS,
                        },
                    ),
                    data={"FILES": excel_file},
                )

                self.assertEqual(response.status_code, 302)

                updated_sac = SingleAuditChecklist.objects.get(pk=sac.id)

                self.assertEqual(
                    updated_sac.additional_eins["AdditionalEINs"]["auditee_uei"],
                    ExcelFileHandlerViewTests.GOOD_UEI,
                )

                self.assertEqual(
                    len(
                        updated_sac.additional_eins["AdditionalEINs"][
                            "additional_eins_entries"
                        ]
                    ),
                    1,
                )

                additional_eins_entries = updated_sac.additional_eins["AdditionalEINs"][
                    "additional_eins_entries"
                ][0]

                self.assertEqual(
                    additional_eins_entries["additional_ein"],
                    test_data[0]["additional_ein"],
                )

    @patch("audit.validators._scan_file")
    def test_valid_file_upload_for_notes_to_sefa(self, mock_scan_file):
        """When a valid Excel file is uploaded, the file should be stored and the SingleAuditChecklist should be updated to include the uploaded Notes to SEFA data"""

        sac = _mock_login_and_scan(self.client, mock_scan_file)
        test_data = json.loads(NOTES_TO_SEFA_ENTRY_FIXTURES.read_text(encoding="utf-8"))

        # add valid data to the workbook
        workbook = load_workbook(NOTES_TO_SEFA_TEMPLATE, data_only=True)
        _set_by_name(workbook, "auditee_uei", ExcelFileHandlerViewTests.GOOD_UEI)
        _set_by_name(workbook, "accounting_policies", "Mandatory notes")
        _set_by_name(workbook, "is_minimis_rate_used", "N")
        _set_by_name(workbook, "rate_explained", "More explanation.")
        _set_by_name(workbook, "section_name", FORM_SECTIONS.NOTES_TO_SEFA)
        _add_entry(workbook, 0, test_data[0])

        with NamedTemporaryFile(suffix=".xlsx") as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)

            with open(tmp.name, "rb") as excel_file:
                response = self.client.post(
                    reverse(
                        f"audit:{FORM_SECTIONS.NOTES_TO_SEFA}",
                        kwargs={
                            "report_id": sac.report_id,
                            "form_section": FORM_SECTIONS.NOTES_TO_SEFA,
                        },
                    ),
                    data={"FILES": excel_file},
                )

                self.assertEqual(response.status_code, 302)

                updated_sac = SingleAuditChecklist.objects.get(pk=sac.id)

                self.assertEqual(
                    updated_sac.notes_to_sefa["NotesToSefa"]["auditee_uei"],
                    ExcelFileHandlerViewTests.GOOD_UEI,
                )

                self.assertEqual(
                    len(
                        updated_sac.notes_to_sefa["NotesToSefa"][
                            "notes_to_sefa_entries"
                        ]
                    ),
                    1,
                )

                notes_to_sefa_entries = updated_sac.notes_to_sefa["NotesToSefa"][
                    "notes_to_sefa_entries"
                ][0]

                self.assertEqual(
                    notes_to_sefa_entries["note_title"],
                    test_data[0]["note_title"],
                )
