import io
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from audit.models import (
    ExcelFile,
    SingleAuditChecklist,
    SingleAuditReportFile,
    generate_sac_report_id,
)

from audit.fixtures.excel import FORM_SECTIONS
from dissemination.test_search import TestMaterializedViewBuilder
from dissemination.models import (
    General,
    FederalAward,
    Finding,
    FindingText,
    CapText,
    Note,
    OneTimeAccess,
)
from users.models import Permission, UserPermission

from model_bakery import baker
from unittest.mock import patch

from datetime import timedelta
from uuid import uuid4

User = get_user_model()


class PdfDownloadViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _make_sac_and_general(self, is_public=True):
        sac = baker.make(
            SingleAuditChecklist,
            report_id=generate_sac_report_id(end_date="2023-12-31"),
        )
        general = baker.make(General, is_public=is_public, report_id=sac.report_id)
        return sac, general

    def test_bad_report_id_returns_404(self):
        url = reverse("dissemination:PdfDownload", kwargs={"report_id": "not-real"})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_not_public_returns_403(self):
        general = baker.make(General, is_public=False)

        url = reverse(
            "dissemination:PdfDownload", kwargs={"report_id": general.report_id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_no_file_returns_404(self):
        sac, general = self._make_sac_and_general()

        url = reverse(
            "dissemination:PdfDownload", kwargs={"report_id": general.report_id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    @patch("dissemination.file_downloads.file_exists")
    def test_file_exists_returns_302(self, mock_file_exists):
        mock_file_exists.return_value = True

        sac, general = self._make_sac_and_general()

        file = baker.make(SingleAuditReportFile, sac=sac)

        url = reverse(
            "dissemination:PdfDownload", kwargs={"report_id": general.report_id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(file.filename, response.url)

    @patch("dissemination.file_downloads.file_exists")
    def test_private_returns_403_for_anonymous(self, mock_file_exists):
        mock_file_exists.return_value = True

        sac, general = self._make_sac_and_general(is_public=False)

        url = reverse(
            "dissemination:PdfDownload", kwargs={"report_id": general.report_id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    @patch("dissemination.file_downloads.file_exists")
    def test_private_returns_403_for_unpermissioned(self, mock_file_exists):
        mock_file_exists.return_value = True

        sac, general = self._make_sac_and_general(is_public=False)

        user = baker.make(User)

        url = reverse(
            "dissemination:PdfDownload", kwargs={"report_id": general.report_id}
        )

        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    @patch("dissemination.file_downloads.file_exists")
    def test_private_returns_302_for_permissioned(self, mock_file_exists):
        mock_file_exists.return_value = True

        sac, general = self._make_sac_and_general(is_public=False)

        user = baker.make(User)
        permission = Permission.objects.get(slug=Permission.PermissionType.READ_TRIBAL)
        baker.make(
            UserPermission,
            email=user.email,
            user=user,
            permission=permission,
        )
        file = baker.make(SingleAuditReportFile, sac=sac)

        url = reverse(
            "dissemination:PdfDownload", kwargs={"report_id": general.report_id}
        )

        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(file.filename, response.url)


class SearchViewTests(TestMaterializedViewBuilder):
    def setUp(self):
        super().setUp()
        self.anon_client = Client()
        self.auth_client = Client()
        self.perm_client = Client()

        self.auth_user = baker.make(User)
        self.auth_client.force_login(self.auth_user)

        self.perm_user = baker.make(User)
        permission = Permission.objects.get(slug=Permission.PermissionType.READ_TRIBAL)
        baker.make(
            UserPermission,
            email=self.perm_user.email,
            user=self.perm_user,
            permission=permission,
        )
        self.perm_client.force_login(self.perm_user)

    def _search_url(self):
        return reverse("dissemination:Search")

    def test_allows_anonymous(self):
        response = self.anon_client.get(self._search_url())
        self.assertEqual(response.status_code, 200)

    def test_search(self):
        response = self.anon_client.post(self._search_url(), {})
        self.assertContains(
            response, "is updated in real time and can be used to confirm"
        )
        # If there are results, we'll see "results in x seconds" somewhere.
        self.assertNotContains(response, "results in")

    def test_anonymous_returns_private_and_public(self):
        """Anonymous users should see all reports (public and private included)."""
        public = baker.make(General, is_public=True, audit_year=2023, _quantity=5)
        private = baker.make(General, is_public=False, audit_year=2023, _quantity=5)
        for p in public:
            baker.make(FederalAward, report_id=p)
        for p in private:
            baker.make(FederalAward, report_id=p)
        self.refresh_materialized_view()
        response = self.anon_client.post(self._search_url(), {})

        # 1-10 of <strong>10</strong> results in x seconds.
        self.assertContains(response, "<strong>10</strong>")

        # all of the public reports should show up on the page
        for p in public:
            self.assertContains(response, p.report_id)

        # all of the private reports should show up on the page
        for p in private:
            self.assertContains(response, p.report_id)

    def test_non_permissioned_returns_private_and_public(self):
        """Non-permissioned users should see all reports (public and private included)."""
        public = baker.make(General, is_public=True, audit_year=2023, _quantity=5)
        private = baker.make(General, is_public=False, audit_year=2023, _quantity=5)
        for p in public:
            baker.make(FederalAward, report_id=p)
        for p in private:
            baker.make(FederalAward, report_id=p)
        self.refresh_materialized_view()
        response = self.auth_client.post(self._search_url(), {})

        # 1-10 of <strong>10</strong> results in x seconds.
        self.assertContains(response, "<strong>10</strong>")

        # all of the public reports should show up on the page
        for p in public:
            self.assertContains(response, p.report_id)

        # all of the private reports should show up on the page
        for p in private:
            self.assertContains(response, p.report_id)

    def test_permissioned_returns_all(self):
        public = baker.make(General, is_public=True, audit_year=2023, _quantity=5)
        private = baker.make(General, is_public=False, audit_year=2023, _quantity=5)
        for p in public:
            baker.make(FederalAward, report_id=p)
        for p in private:
            baker.make(FederalAward, report_id=p)
        self.refresh_materialized_view()

        response = self.perm_client.post(self._search_url(), {})

        # 1-10 of <strong>10</strong> results in x seconds.
        self.assertContains(response, "<strong>10</strong>")

        # all of the public reports should show up on the page
        for p in public:
            self.assertContains(response, p.report_id)

        # all of the private reports should show up on the page
        for p in private:
            self.assertContains(response, p.report_id)


class OneTimeAccessDownloadViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_malformed_uuid_returns_400(self):
        """
        Given a malformed UUID
        When a request is sent to the OTA download url
        Then the response should be 400
        """
        url = reverse("dissemination:OtaPdfDownload", kwargs={"uuid": "not-a-uuid"})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)

    def test_bad_uuid_returns_404(self):
        """
        Given a UUID that does not match an existing OTA record
        When a request is sent to the OTA download url
        Then the response should be 404
        """
        uuid = uuid4()
        url = reverse("dissemination:OtaPdfDownload", kwargs={"uuid": uuid})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_expired_uuid_returns_404(self):
        """
        Given a UUID that has expired
        When a request is sent to the OTA download url
        Then the response should be 404
        """
        uuid = uuid4()

        sac = baker.make(
            SingleAuditChecklist,
            report_id=generate_sac_report_id(end_date="2024-01-31"),
        )
        baker.make(SingleAuditReportFile, sac=sac)
        ota = baker.make(OneTimeAccess, uuid=uuid, report_id=sac.report_id)

        # override the OTA timestamp to something that is outside the expiry window
        timestamp = timezone.now() - timedelta(
            seconds=(settings.ONE_TIME_ACCESS_TTL_SECS + 5)
        )
        ota.timestamp = timestamp
        ota.save()

        url = reverse("dissemination:OtaPdfDownload", kwargs={"uuid": uuid})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_no_sac_returns_404(self):
        """
        Given a UUID for an OTA that references a non-existent SAC
        When a request is sent to the OTA download url
        Then the response should be 404
        """
        uuid = uuid4()

        report_id = generate_sac_report_id(end_date="2024-01-31")
        baker.make(OneTimeAccess, uuid=uuid, report_id=report_id)

        url = reverse("dissemination:OtaPdfDownload", kwargs={"uuid": uuid})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_no_pdf_returns_404(self):
        """
        Given a UUID for an OTA that references a SAC with no SingleAuditReport PDF
        When a request is sent to the OTA download url
        Then the response should be 404
        """
        uuid = uuid4()

        sac = baker.make(
            SingleAuditChecklist,
            report_id=generate_sac_report_id(end_date="2024-01-31"),
        )
        baker.make(OneTimeAccess, uuid=uuid, report_id=sac.report_id)

        url = reverse("dissemination:OtaPdfDownload", kwargs={"uuid": uuid})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    @patch("dissemination.file_downloads.file_exists")
    def test_good_uuid_returns_redirect(self, mock_file_exists):
        """
        Given a UUID that does match an existing OTA record
        When a request is sent to the OTA download url
        Then the response should be a 302 redirect to an S3 download url
        When a second request is sent to the OTA download url
        Then the response should be 404
        """
        mock_file_exists.return_value = True
        uuid = uuid4()

        sac = baker.make(
            SingleAuditChecklist,
            report_id=generate_sac_report_id(end_date="2024-01-31"),
        )
        baker.make(SingleAuditReportFile, sac=sac)
        baker.make(OneTimeAccess, uuid=uuid, report_id=sac.report_id)

        url = reverse("dissemination:OtaPdfDownload", kwargs={"uuid": uuid})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(sac.report_id, response.url)

        response_2 = self.client.get(url)

        self.assertEqual(response_2.status_code, 404)


class XlsxDownloadViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _make_sac_and_general(self, is_public=True):
        sac = baker.make(
            SingleAuditChecklist,
            report_id=generate_sac_report_id(end_date="2023-12-31"),
        )
        general = baker.make(General, is_public=is_public, report_id=sac.report_id)
        return sac, general

    def test_bad_report_id_returns_404(self):
        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={"report_id": "not-real", "file_type": FORM_SECTIONS.FEDERAL_AWARDS},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_not_public_returns_403_for_anon(self):
        general = baker.make(General, is_public=False)

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": general.report_id,
                "file_type": FORM_SECTIONS.FEDERAL_AWARDS,
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_no_file_returns_404(self):
        sac, general = self._make_sac_and_general()

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": general.report_id,
                "file_type": FORM_SECTIONS.FEDERAL_AWARDS,
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    @patch("dissemination.file_downloads.file_exists")
    def test_file_exists_returns_302(self, mock_file_exists):
        mock_file_exists.return_value = True

        sac, general = self._make_sac_and_general()

        file = baker.make(ExcelFile, sac=sac, form_section=FORM_SECTIONS.FEDERAL_AWARDS)

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": general.report_id,
                "file_type": FORM_SECTIONS.FEDERAL_AWARDS,
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(file.filename, response.url)

    @patch("dissemination.file_downloads.file_exists")
    def test_private_returns_403_for_anonymous(self, mock_file_exists):
        mock_file_exists.return_value = True

        sac, general = self._make_sac_and_general(is_public=False)

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": general.report_id,
                "file_type": FORM_SECTIONS.FEDERAL_AWARDS,
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    @patch("dissemination.file_downloads.file_exists")
    def test_private_returns_403_for_unpermissioned(self, mock_file_exists):
        mock_file_exists.return_value = True

        sac, general = self._make_sac_and_general(is_public=False)

        user = baker.make(User)

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": general.report_id,
                "file_type": FORM_SECTIONS.FEDERAL_AWARDS,
            },
        )

        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    @patch("dissemination.file_downloads.file_exists")
    def test_private_returns_302_for_permissioned(self, mock_file_exists):
        mock_file_exists.return_value = True

        sac, general = self._make_sac_and_general(is_public=False)

        user = baker.make(User)
        permission = Permission.objects.get(slug=Permission.PermissionType.READ_TRIBAL)
        baker.make(
            UserPermission,
            email=user.email,
            user=user,
            permission=permission,
        )
        file = baker.make(ExcelFile, sac=sac, form_section=FORM_SECTIONS.FEDERAL_AWARDS)

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": general.report_id,
                "file_type": FORM_SECTIONS.FEDERAL_AWARDS,
            },
        )

        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(file.filename, response.url)


class SummaryViewTests(TestMaterializedViewBuilder):
    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_public_summary(self):
        """
        A public audit should have a viewable summary, and returns 200.
        """
        baker.make(General, report_id="2022-12-GSAFAC-0000000001", is_public=True)
        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_private_summary(self):
        """
        Anonymous requests for private audit summaries should return 200
        """
        baker.make(General, report_id="2022-12-GSAFAC-0000000001", is_public=False)
        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_permissioned_private_summary(self):
        """
        Permissioned requests for private audit summaries should return 200
        """
        general = baker.make(General, is_public=False)
        user = baker.make(User)

        permission = Permission.objects.get(slug=Permission.PermissionType.READ_TRIBAL)
        baker.make(UserPermission, user=user, email=user.email, permission=permission)

        url = reverse("dissemination:Summary", kwargs={"report_id": general.report_id})

        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_summary_context(self):
        """
        The summary context should include the same data that is in the models.
        Create a bunch of fake DB data under the same report_id. Then, check a few
        fields in the context for the summary page to verify that the fake data persists.
        """
        gen = baker.make(General, report_id="2022-12-GSAFAC-0000000001", is_public=True)
        award = baker.make(FederalAward, report_id=gen)
        finding = baker.make(Finding, report_id=gen)
        finding_text = baker.make(FindingText, report_id=gen)
        cap_text = baker.make(CapText, report_id=gen)
        note = baker.make(Note, report_id=gen)

        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)
        self.assertEqual(
            response.context["data"]["Awards"][0]["additional_award_identification"],
            award.additional_award_identification,
        )
        self.assertEqual(
            response.context["data"]["Audit Findings"][0]["reference_number"],
            finding.reference_number,
        )
        self.assertEqual(
            response.context["data"]["Audit Findings Text"][0]["finding_ref_number"],
            finding_text.finding_ref_number,
        )
        self.assertEqual(
            response.context["data"]["Corrective Action Plan"][0][
                "contains_chart_or_table"
            ],
            cap_text.contains_chart_or_table,
        )
        self.assertEqual(
            response.context["data"]["Notes to SEFA"][0]["accounting_policies"],
            note.accounting_policies,
        )

    def test_distinct_findings_by_reference_number(self):
        """
        Test that the Audit Findings in the context only include distinct findings
        based on the `reference_number` for a given report_id.
        """
        gen = baker.make(General, report_id="2022-12-GSAFAC-0000000001", is_public=True)

        # Create multiple findings with the same reference_number
        baker.make(Finding, report_id=gen, reference_number="REF001")
        baker.make(Finding, report_id=gen, reference_number="REF001")
        baker.make(Finding, report_id=gen, reference_number="REF002")

        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)

        # Verify that the response contains only distinct reference_numbers
        findings = response.context["data"]["Audit Findings"]
        reference_numbers = [finding["reference_number"] for finding in findings]
        self.assertEqual(len(reference_numbers), len(set(reference_numbers)))
        self.assertIn("REF001", reference_numbers)
        self.assertIn("REF002", reference_numbers)
        self.assertEqual(len(reference_numbers), 2)  # Only 2 distinct reference numbers

    def test_unique_findings_no_duplicates(self):
        """
        Test that the Audit Findings in the context include all findings
        when all `reference_number` values are unique for a given report_id.
        """
        gen = baker.make(General, report_id="2022-12-GSAFAC-0000000002", is_public=True)

        # findings with unique reference_numbers
        baker.make(Finding, report_id=gen, reference_number="REF003")
        baker.make(Finding, report_id=gen, reference_number="REF004")

        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000002"}
        )

        response = self.client.get(url)

        # Verify that all unique reference_numbers are present
        findings = response.context["data"]["Audit Findings"]
        reference_numbers = [finding["reference_number"] for finding in findings]
        self.assertEqual(len(reference_numbers), 2)  # all findings are returned
        self.assertIn("REF003", reference_numbers)
        self.assertIn("REF004", reference_numbers)

    def test_sac_download_available(self):
        """
        Ensures is_sf_sac_downloadable is True when a submission's SF-SAC is downloadable
        """
        gen_object = baker.make(
            General, is_public=True, report_id="2022-12-GSAFAC-0000000001"
        )
        baker.make(
            FederalAward,
            report_id=gen_object,
        )
        self.refresh_materialized_view()
        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)
        self.assertEqual(response.context["is_sf_sac_downloadable"], True)

    def test_sac_download_not_available(self):
        """
        Ensures is_sf_sac_downloadable is False when a submission's SF-SAC is not downloadable
        """
        baker.make(General, report_id="2022-12-GSAFAC-0000000001", is_public=True)
        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)
        self.assertEqual(response.context["is_sf_sac_downloadable"], False)


class SummaryReportDownloadViewTests(TestMaterializedViewBuilder):
    def setUp(self):
        super().setUp()
        self.anon_client = Client()
        self.perm_client = Client()

        self.perm_user = baker.make(User)
        permission = Permission.objects.get(slug=Permission.PermissionType.READ_TRIBAL)
        baker.make(
            UserPermission,
            email=self.perm_user.email,
            user=self.perm_user,
            permission=permission,
        )
        self.perm_client.force_login(self.perm_user)

    def _make_general(self, is_public=True, **kwargs):
        """
        Create a General object in dissemination with the keyword arguments passed in.
        """
        general = baker.make(
            General,
            is_public=is_public,
            **kwargs,
        )
        return general

    def _summary_report_url(self):
        return reverse("dissemination:MultipleSummaryReportDownload")

    def _mock_filename(self):
        return "some-report-name.xlsx", None

    def _mock_download_url(self):
        return "http://example.com/gsa-fac-private-s3/temp/some-report-name.xlsx"

    @patch("dissemination.summary_reports.prepare_workbook_for_download")
    def test_bad_search_returns_400(self, mock_prepare_workbook_for_download):
        """
        Submitting a form with bad parameters should throw a BadRequest.
        """
        response = self.anon_client.post(
            self._summary_report_url(), {"start_date": "Not a date"}
        )
        self.assertEqual(response.status_code, 400)

    @patch("dissemination.summary_reports.prepare_workbook_for_download")
    def test_empty_results_returns_404(self, mock_prepare_workbook_for_download):
        """
        Searches with no results should return a 404, not an empty excel file.
        """
        general = self._make_general(is_public=False, auditee_uei="123456789012")
        baker.make(FederalAward, report_id=general)
        self.refresh_materialized_view()
        response = self.anon_client.post(
            self._summary_report_url(), {"uei_or_ein": "NotTheOther1"}
        )
        self.assertEqual(response.status_code, 404)

    @patch("dissemination.summary_reports.prepare_workbook_for_download")
    def test_authorized_user_with_private_data(
        self, mock_prepare_workbook_for_download
    ):
        """Test that an authorized user can access private data."""
        mock_filename = "mocked-report.xlsx"
        mock_workbook_bytes = io.BytesIO(b"fake file content")
        mock_prepare_workbook_for_download.return_value = (
            mock_filename,
            mock_workbook_bytes,
            1.0,
        )

        general = self._make_general(is_public=False)
        baker.make(FederalAward, report_id=general)
        baker.make(FindingText, report_id=general)
        self.refresh_materialized_view()

        response = self.perm_client.post(self._summary_report_url(), {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn(
            f"attachment; filename={mock_filename}", response["Content-Disposition"]
        )
        self.assertEqual(response.content, b"fake file content")

    @patch("dissemination.summary_reports.prepare_workbook_for_download")
    def test_unauthorized_user_with_private_data(
        self, mock_prepare_workbook_for_download
    ):
        """Test that an unauthorized user can still receive a file, but without private data."""
        mock_filename = "mocked-report.xlsx"
        mock_workbook_bytes = io.BytesIO(b"fake file content")
        mock_prepare_workbook_for_download.return_value = (
            mock_filename,
            mock_workbook_bytes,
            1.0,
        )

        general = self._make_general(is_public=False)
        baker.make(FederalAward, report_id=general)
        baker.make(FindingText, report_id=general)
        self.refresh_materialized_view()

        response = self.anon_client.post(self._summary_report_url(), {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn(
            f"attachment; filename={mock_filename}", response["Content-Disposition"]
        )
        self.assertEqual(response.content, b"fake file content")

    @patch("dissemination.summary_reports.prepare_workbook_for_download")
    def test_authorized_user_with_public_data(self, mock_prepare_workbook_for_download):
        """Test that an authorized user can access public data."""
        mock_filename = "mocked-report.xlsx"
        mock_workbook_bytes = io.BytesIO(b"fake file content")
        mock_prepare_workbook_for_download.return_value = (
            mock_filename,
            mock_workbook_bytes,
            1.0,
        )

        general = self._make_general(is_public=True)
        baker.make(FederalAward, report_id=general)
        baker.make(FindingText, report_id=general)
        self.refresh_materialized_view()

        response = self.perm_client.post(self._summary_report_url(), {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn(
            f"attachment; filename={mock_filename}", response["Content-Disposition"]
        )
        self.assertEqual(response.content, b"fake file content")

    @patch("dissemination.summary_reports.prepare_workbook_for_download")
    def test_unauthorized_user_with_public_data(
        self, mock_prepare_workbook_for_download
    ):
        """Test that an unauthorized user can access public data."""
        mock_filename = "mocked-report.xlsx"
        mock_workbook_bytes = io.BytesIO(b"fake file content")
        mock_prepare_workbook_for_download.return_value = (
            mock_filename,
            mock_workbook_bytes,
            1.0,
        )

        general = self._make_general(is_public=True)
        baker.make(FederalAward, report_id=general)
        baker.make(FindingText, report_id=general)
        self.refresh_materialized_view()

        response = self.anon_client.post(self._summary_report_url(), {})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn(
            f"attachment; filename={mock_filename}", response["Content-Disposition"]
        )
        self.assertEqual(response.content, b"fake file content")

    @patch("dissemination.summary_reports.prepare_workbook_for_download")
    def test_empty_search_params_returns_file(self, mock_prepare_workbook_for_download):
        """
        File should be generated on empty search parameters ("search all").
        """
        mock_filename = "mocked-report.xlsx"
        mock_workbook_bytes = io.BytesIO(b"fake file content")
        mock_prepare_workbook_for_download.return_value = (
            mock_filename,
            mock_workbook_bytes,
            1.0,
        )
        general = self._make_general(is_public=True)
        baker.make(FederalAward, report_id=general)
        self.refresh_materialized_view()

        response = self.anon_client.post(self._summary_report_url(), {})

        mock_prepare_workbook_for_download.assert_called_once()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertIn(
            f"attachment; filename={mock_filename}", response["Content-Disposition"]
        )
        self.assertEqual(response.content, b"fake file content")

    @patch("dissemination.summary_reports.prepare_workbook_for_download")
    def test_many_results_returns_file(self, mock_prepare_workbook_for_download):
        """
        File should still be generated if there are above SUMMARY_REPORT_DOWNLOAD_LIMIT total results.
        """
        mock_filename = "mocked-report.xlsx"
        mock_workbook_bytes = io.BytesIO(b"fake file content")
        mock_prepare_workbook_for_download.return_value = (
            mock_filename,
            mock_workbook_bytes,
            1.0,
        )

        for i in range(4):
            general = self._make_general(
                is_public=True,
                report_id=generate_sac_report_id(end_date="2023-12-31", count=str(i)),
            )
            baker.make(FederalAward, report_id=general)
        self.refresh_materialized_view()

        with self.settings(SUMMARY_REPORT_DOWNLOAD_LIMIT=2):
            response = self.anon_client.post(self._summary_report_url(), {})
            mock_prepare_workbook_for_download.assert_called_once()

            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                response["Content-Type"],
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            self.assertIn(
                f"attachment; filename={mock_filename}", response["Content-Disposition"]
            )

            self.assertEqual(response.content, b"fake file content")


class PageHandlingTests(TestCase):
    """Test cases for ensuring page handling logic in AdvancedSearch and Search views"""

    def setUp(self):
        """Set up test client and sample form data"""
        self.client = Client()
        self.advanced_search_url = reverse("dissemination:AdvancedSearch")
        self.basic_search_url = reverse("dissemination:Search")

        self.valid_post_data = {
            "audit_year": ["2023"],
            "limit": "10",
            "order_by": "name",
            "order_direction": "asc",
            "page": "1",
        }

    @patch("dissemination.views.run_search")
    def test_advanced_search_post_page_too_high(self, mock_run_search):
        """Ensure page resets to 1 when the requested page is greater than available pages"""
        mock_run_search.return_value.count.return_value = (
            5  # Mock result count (only 1 page available)
        )

        invalid_data = self.valid_post_data.copy()
        invalid_data["page"] = "100"  # Too high

        response = self.client.post(self.advanced_search_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page"], 1)  # Should reset to 1

    @patch("dissemination.views.run_search")
    def test_advanced_search_post_page_zero(self, mock_run_search):
        """Ensure page resets to 1 when the requested page is zero"""
        mock_run_search.return_value.count.return_value = 5

        invalid_data = self.valid_post_data.copy()
        invalid_data["page"] = "0"

        response = self.client.post(self.advanced_search_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page"], 1)  # Should reset to 1

    @patch("dissemination.views.run_search")
    def test_advanced_search_post_page_empty(self, mock_run_search):
        """Ensure page defaults to 1 when no page is provided"""
        mock_run_search.return_value.count.return_value = 5

        invalid_data = self.valid_post_data.copy()
        invalid_data["page"] = ""

        response = self.client.post(self.advanced_search_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page"], 1)  # Should default to 1

    @patch("dissemination.views.run_search")
    def test_advanced_search_post_valid_page(self, mock_run_search):
        """Ensure valid page number remains unchanged"""
        mock_run_search.return_value.count.return_value = 20  # Multiple pages exist

        valid_data = self.valid_post_data.copy()
        valid_data["page"] = "2"  # Valid page

        response = self.client.post(self.advanced_search_url, valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page"], 2)  # Should remain 2
