from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from audit.models import (
    ExcelFile,
    SingleAuditChecklist,
    SingleAuditReportFile,
    generate_sac_report_id,
)
from dissemination.models import General
from users.models import Permission, UserPermission

from model_bakery import baker
from unittest.mock import patch

User = get_user_model()


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


class SearchViewTests(TestCase):
    def setUp(self):
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
        self.assertContains(response, "Search single audit reports")
        self.assertNotContains(response, "Results: ")

    def test_anonymous_returns_only_public(self):
        public = baker.make(General, is_public=True, _quantity=5)
        private = baker.make(General, is_public=False, _quantity=5)

        response = self.anon_client.post(self._search_url(), {})

        self.assertContains(response, "Results: 5")

        for p in public:
            self.assertContains(response, p.report_id)

        for p in private:
            self.assertNotContains(response, p.report_id)

    def test_non_permissioned_returns_only_public(self):
        public = baker.make(General, is_public=True, _quantity=5)
        private = baker.make(General, is_public=False, _quantity=5)

        response = self.auth_client.post(self._search_url(), {})

        self.assertContains(response, "Results: 5")

        for p in public:
            self.assertContains(response, p.report_id)

        for p in private:
            self.assertNotContains(response, p.report_id)

    def test_permissioned_returns_all(self):
        public = baker.make(General, is_public=True, _quantity=5)
        private = baker.make(General, is_public=False, _quantity=5)

        response = self.perm_client.post(self._search_url(), {})

        self.assertContains(response, "Results: 10")

        for p in public:
            self.assertContains(response, p.report_id)

        for p in private:
            self.assertContains(response, p.report_id)


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
