from django.test import Client, TestCase
from django.urls import reverse

from audit.models import (
    ExcelFile,
    SingleAuditChecklist,
    SingleAuditReportFile,
    generate_sac_report_id,
)
from dissemination.models import General

from model_bakery import baker
from unittest.mock import patch


class PdfDownloadViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _make_sac_and_general(self):
        sac = baker.make(
            SingleAuditChecklist,
            report_id=generate_sac_report_id(end_date="2023-12-31"),
        )
        general = baker.make(General, is_public=True, report_id=sac.report_id)
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

    @patch("audit.file_downloads.file_exists")
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


class XlsxDownloadViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def _make_sac_and_general(self):
        sac = baker.make(
            SingleAuditChecklist,
            report_id=generate_sac_report_id(end_date="2023-12-31"),
        )
        general = baker.make(General, is_public=True, report_id=sac.report_id)
        return sac, general

    def test_bad_report_id_returns_404(self):
        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={"report_id": "not-real", "file_type": "FederalAwardsExpended"},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_not_public_returns_403(self):
        general = baker.make(General, is_public=False)

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": general.report_id,
                "file_type": "FederalAwardsExpended",
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
                "file_type": "FederalAwardsExpended",
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    @patch("audit.file_downloads.file_exists")
    def test_file_exists_returns_302(self, mock_file_exists):
        mock_file_exists.return_value = True

        sac, general = self._make_sac_and_general()

        file = baker.make(ExcelFile, sac=sac, form_section="FederalAwardsExpended")

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": general.report_id,
                "file_type": "FederalAwardsExpended",
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(file.filename, response.url)
