from django.http import HttpResponseRedirect
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from django.test import Client
from model_bakery import baker
from unittest.mock import patch

from tempfile import NamedTemporaryFile

from openpyxl import load_workbook
from openpyxl.cell import Cell

from .fixtures.excel import (
    FEDERAL_AWARDS_TEMPLATE,
    CORRECTIVE_ACTION_PLAN_TEMPLATE,
    FINDINGS_TEXT_TEMPLATE,
    FINDINGS_UNIFORM_GUIDANCE_TEMPLATE,
    CORRECTIVE_ACTION_PLAN_ENTRY_FIXTURES,
    FINDINGS_TEXT_ENTRY_FIXTURES,
    FINDINGS_UNIFORM_GUIDANCE_ENTRY_FIXTURES,
    FEDERAL_AWARDS_ENTRY_FIXTURES,
    FEDERAL_AWARDS_EXPENDED,
    CORRECTIVE_ACTION_PLAN,
    FINDINGS_TEXT,
    FINDINGS_UNIFORM_GUIDANCE,
)
from .models import Access, SingleAuditChecklist
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
    "certifying_auditee_contact": "a@a.com",
    "certifying_auditor_contact": "b@b.com",
    "auditee_contacts": ["c@c.com"],
    "auditor_contacts": ["d@d.com"],
}

EXCEL_FILES = [
    CORRECTIVE_ACTION_PLAN,
    FEDERAL_AWARDS_EXPENDED,
    FINDINGS_UNIFORM_GUIDANCE,
    FINDINGS_TEXT,
]


# Mocking the user login and file scan functions
def _mock_login_and_scan(self, mock_scan_file):
    """Helper function to mock the login and file scan functions"""
    user = baker.make(User)

    sac = baker.make(SingleAuditChecklist)

    baker.make(Access, user=user, sac=sac)

    self.client.force_login(user)

    # mock the call to the external AV service
    mock_scan_file.return_value = MockHttpResponse(200, "clean!")

    return sac


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

        self.client.post(f"/audit/ready-for-certification/{report_id}", data={})
        data = MySubmissions.fetch_my_submissions(self.user)
        self.assertEqual(data[0]["submission_status"], "ready_for_certification")


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
    def test_login_required(self):
        """When an unauthenticated request is made"""

        for form_section in EXCEL_FILES:
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

        for form_section in EXCEL_FILES:
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
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)

        self.client.force_login(user)
        for form_section in EXCEL_FILES:
            response = self.client.post(
                reverse(
                    f"audit:{form_section}",
                    kwargs={"report_id": sac.report_id, "form_section": form_section},
                )
            )

            self.assertEqual(response.status_code, 403)

    def test_no_file_attached_returns_400(self):
        """When a request is made with no file attached, a 400 error should be returned"""
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)
        baker.make(Access, user=user, sac=sac)

        self.client.force_login(user)

        for form_section in EXCEL_FILES:
            response = self.client.post(
                reverse(
                    f"audit:{form_section}",
                    kwargs={"report_id": sac.report_id, "form_section": form_section},
                )
            )

            self.assertEqual(response.status_code, 400)

    def test_invalid_file_upload_returns_400(self):
        """When an invalid Excel file is uploaded, a 400 error should be returned"""
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)
        baker.make(Access, user=user, sac=sac)

        self.client.force_login(user)

        file = SimpleUploadedFile("not-excel.txt", b"asdf", "text/plain")

        for form_section in EXCEL_FILES:
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

        sac = _mock_login_and_scan(self, mock_scan_file)

        # add valid data to the workbook
        workbook = load_workbook(FEDERAL_AWARDS_TEMPLATE, data_only=True)
        _set_by_name(workbook, "auditee_ein", "123456789")
        _set_by_name(workbook, "total_amount_expended", 200)
        _add_entry(workbook, 0, FEDERAL_AWARDS_ENTRY_FIXTURES[0])

        with NamedTemporaryFile(suffix=".xlsx") as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)

            with open(tmp.name, "rb") as excel_file:
                response = self.client.post(
                    reverse(
                        f"audit:{EXCEL_FILES[1]}",
                        kwargs={
                            "report_id": sac.report_id,
                            "form_section": EXCEL_FILES[1],
                        },
                    ),
                    data={"FILES": excel_file},
                )

                self.assertEqual(response.status_code, 302)

                updated_sac = SingleAuditChecklist.objects.get(pk=sac.id)

                self.assertEqual(
                    updated_sac.federal_awards["FederalAwards"]["auditee_ein"],
                    "123456789",
                )
                self.assertEqual(
                    updated_sac.federal_awards["FederalAwards"][
                        "total_amount_expended"
                    ],
                    200,
                )
                self.assertEqual(
                    len(updated_sac.federal_awards["FederalAwards"]["federal_awards"]),
                    1,
                )

                federal_awards_entry = updated_sac.federal_awards["FederalAwards"][
                    "federal_awards"
                ][0]

                self.assertEqual(
                    federal_awards_entry["cluster"]["name"],
                    FEDERAL_AWARDS_ENTRY_FIXTURES[0]["cluster_name"],
                )
                self.assertEqual(
                    federal_awards_entry["direct_or_indirect_award"]["is_direct"],
                    FEDERAL_AWARDS_ENTRY_FIXTURES[0]["direct_award"],
                )
                self.assertEqual(
                    federal_awards_entry["program"]["is_major"],
                    FEDERAL_AWARDS_ENTRY_FIXTURES[0]["major_program"],
                )
                self.assertEqual(
                    federal_awards_entry["program"]["number"],
                    FEDERAL_AWARDS_ENTRY_FIXTURES[0]["program_number"],
                )
                self.assertEqual(
                    federal_awards_entry["amount_expended"],
                    FEDERAL_AWARDS_ENTRY_FIXTURES[0]["amount_expended"],
                )
                self.assertEqual(
                    federal_awards_entry["program"]["name"],
                    FEDERAL_AWARDS_ENTRY_FIXTURES[0]["federal_program_name"],
                )
                self.assertEqual(
                    federal_awards_entry["loan_or_loan_guarantee"]["is_guaranteed"],
                    FEDERAL_AWARDS_ENTRY_FIXTURES[0]["loan_or_loan_guarantee"],
                )
                self.assertEqual(
                    federal_awards_entry["program"]["number_of_audit_findings"],
                    FEDERAL_AWARDS_ENTRY_FIXTURES[0]["number_of_audit_findings"],
                )
                self.assertEqual(
                    federal_awards_entry["program"]["audit_report_type"],
                    FEDERAL_AWARDS_ENTRY_FIXTURES[0]["major_program_audit_report_type"],
                )
                self.assertEqual(
                    federal_awards_entry["loan_or_loan_guarantee"][
                        "loan_balance_at_audit_period_end"
                    ],
                    FEDERAL_AWARDS_ENTRY_FIXTURES[0][
                        "loan_balance_at_audit_period_end"
                    ],
                )
                self.assertEqual(
                    federal_awards_entry["subrecipients"]["is_passed"],
                    FEDERAL_AWARDS_ENTRY_FIXTURES[0][
                        "federal_award_passed_to_subrecipients"
                    ],
                )
                self.assertEqual(
                    federal_awards_entry["subrecipients"]["amount"],
                    FEDERAL_AWARDS_ENTRY_FIXTURES[0][
                        "federal_award_passed_to_subrecipients_amount"
                    ],
                )
                self.assertEqual(
                    federal_awards_entry["direct_or_indirect_award"]["entities"],
                    [
                        {"name": "A", "identifying_number": "1"},
                        {"name": "B", "identifying_number": "2"},
                    ],
                )

    @patch("audit.validators._scan_file")
    def test_valid_file_upload_for_corrective_action_plan(self, mock_scan_file):
        """When a valid Excel file is uploaded, the file should be stored and the SingleAuditChecklist should be updated to include the uploaded Corrective Action Plan data"""

        sac = _mock_login_and_scan(self, mock_scan_file)

        # add valid data to the workbook
        workbook = load_workbook(CORRECTIVE_ACTION_PLAN_TEMPLATE, data_only=True)
        _set_by_name(workbook, "auditee_ein", "123456789")

        _add_entry(workbook, 0, CORRECTIVE_ACTION_PLAN_ENTRY_FIXTURES[0])

        with NamedTemporaryFile(suffix=".xlsx") as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)

            with open(tmp.name, "rb") as excel_file:
                response = self.client.post(
                    reverse(
                        f"audit:{EXCEL_FILES[0]}",
                        kwargs={
                            "report_id": sac.report_id,
                            "form_section": EXCEL_FILES[0],
                        },
                    ),
                    data={"FILES": excel_file},
                )

                self.assertEqual(response.status_code, 302)

                updated_sac = SingleAuditChecklist.objects.get(pk=sac.id)

                self.assertEqual(
                    updated_sac.corrective_action_plan["CorrectiveActionPlan"][
                        "auditee_ein"
                    ],
                    "123456789",
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
                    CORRECTIVE_ACTION_PLAN_ENTRY_FIXTURES[0]["planned_action"],
                )
                self.assertEqual(
                    corrective_action_plan_entry["reference_number"],
                    CORRECTIVE_ACTION_PLAN_ENTRY_FIXTURES[0]["reference_number"],
                )

    @patch("audit.validators._scan_file")
    def test_valid_file_upload_for_findings_uniform_guidance(self, mock_scan_file):
        """When a valid Excel file is uploaded, the file should be stored and the SingleAuditChecklist should be updated to include the uploaded Findings Uniform Guidance data"""

        sac = _mock_login_and_scan(self, mock_scan_file)

        # add valid data to the workbook
        workbook = load_workbook(FINDINGS_UNIFORM_GUIDANCE_TEMPLATE, data_only=True)
        _set_by_name(workbook, "auditee_ein", "123456789")

        _add_entry(workbook, 0, FINDINGS_UNIFORM_GUIDANCE_ENTRY_FIXTURES[0])

        with NamedTemporaryFile(suffix=".xlsx") as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)

            with open(tmp.name, "rb") as excel_file:
                response = self.client.post(
                    reverse(
                        f"audit:{EXCEL_FILES[2]}",
                        kwargs={
                            "report_id": sac.report_id,
                            "form_section": EXCEL_FILES[2],
                        },
                    ),
                    data={"FILES": excel_file},
                )

                self.assertEqual(response.status_code, 302)

                updated_sac = SingleAuditChecklist.objects.get(pk=sac.id)

                self.assertEqual(
                    updated_sac.findings_uniform_guidance["FindingsUniformGuidance"][
                        "auditee_ein"
                    ],
                    "123456789",
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
                    findings_entries["program"]["number"],
                    FINDINGS_UNIFORM_GUIDANCE_ENTRY_FIXTURES[0]["program_number"],
                )
                self.assertEqual(
                    findings_entries["program"]["compliance_requirement"],
                    FINDINGS_UNIFORM_GUIDANCE_ENTRY_FIXTURES[0][
                        "compliance_requirement"
                    ],
                )
                self.assertEqual(
                    findings_entries["findings"]["repeat_prior_reference"],
                    FINDINGS_UNIFORM_GUIDANCE_ENTRY_FIXTURES[0][
                        "repeat_prior_reference"
                    ],
                )
                self.assertEqual(
                    findings_entries["findings"]["reference"],
                    FINDINGS_UNIFORM_GUIDANCE_ENTRY_FIXTURES[0][
                        "finding_reference_number"
                    ],
                )
                self.assertEqual(
                    findings_entries["modified_opinion"],
                    FINDINGS_UNIFORM_GUIDANCE_ENTRY_FIXTURES[0]["modified_opinion"],
                )

    @patch("audit.validators._scan_file")
    def test_valid_file_upload_for_findings_text(self, mock_scan_file):
        """When a valid Excel file is uploaded, the file should be stored and the SingleAuditChecklist should be updated to include the uploaded Findings Text data"""

        sac = _mock_login_and_scan(self, mock_scan_file)

        # add valid data to the workbook
        workbook = load_workbook(FINDINGS_TEXT_TEMPLATE, data_only=True)
        _set_by_name(workbook, "auditee_ein", "123456789")

        _add_entry(workbook, 0, FINDINGS_TEXT_ENTRY_FIXTURES[0])

        with NamedTemporaryFile(suffix=".xlsx") as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)

            with open(tmp.name, "rb") as excel_file:
                response = self.client.post(
                    reverse(
                        f"audit:{EXCEL_FILES[3]}",
                        kwargs={
                            "report_id": sac.report_id,
                            "form_section": EXCEL_FILES[3],
                        },
                    ),
                    data={"FILES": excel_file},
                )

                self.assertEqual(response.status_code, 302)

                updated_sac = SingleAuditChecklist.objects.get(pk=sac.id)

                self.assertEqual(
                    updated_sac.findings_text["FindingsText"]["auditee_ein"],
                    "123456789",
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
                    FINDINGS_TEXT_ENTRY_FIXTURES[0]["contains_chart_or_table"],
                )
                self.assertEqual(
                    findings_entries["text_of_finding"],
                    FINDINGS_TEXT_ENTRY_FIXTURES[0]["text_of_finding"],
                )
                self.assertEqual(
                    findings_entries["reference_number"],
                    FINDINGS_TEXT_ENTRY_FIXTURES[0]["reference_number"],
                )
