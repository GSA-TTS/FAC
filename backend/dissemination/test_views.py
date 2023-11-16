from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from audit.models import (
    ExcelFile,
    SingleAuditChecklist,
    SingleAuditReportFile,
    generate_sac_report_id,
)
from dissemination.models import (
    General,
    FederalAward,
    Finding,
    FindingText,
    CapText,
    Note,
)
from users.models import Permission, UserPermission

from model_bakery import baker
from unittest.mock import patch

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

    @patch("audit.file_downloads.file_exists")
    def test_private_returns_403_for_anonymous(self, mock_file_exists):
        mock_file_exists.return_value = True

        sac, general = self._make_sac_and_general(is_public=False)

        url = reverse(
            "dissemination:PdfDownload", kwargs={"report_id": general.report_id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    @patch("audit.file_downloads.file_exists")
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

    @patch("audit.file_downloads.file_exists")
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

        # all of the public reports should show up on the page
        for p in public:
            self.assertContains(response, p.report_id)

        # none of the private reports should show up on the page
        for p in private:
            self.assertNotContains(response, p.report_id)

    def test_non_permissioned_returns_only_public(self):
        public = baker.make(General, is_public=True, _quantity=5)
        private = baker.make(General, is_public=False, _quantity=5)

        response = self.auth_client.post(self._search_url(), {})

        self.assertContains(response, "Results: 5")

        # all of the public reports should show up on the page
        for p in public:
            self.assertContains(response, p.report_id)

        # none of the private reports should show up on the page
        for p in private:
            self.assertNotContains(response, p.report_id)

    def test_permissioned_returns_all(self):
        public = baker.make(General, is_public=True, _quantity=5)
        private = baker.make(General, is_public=False, _quantity=5)

        response = self.perm_client.post(self._search_url(), {})

        self.assertContains(response, "Results: 10")

        # all of the public reports should show up on the page
        for p in public:
            self.assertContains(response, p.report_id)

        # all of the private reports should show up on the page
        for p in private:
            self.assertContains(response, p.report_id)


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
            kwargs={"report_id": "not-real", "file_type": "FederalAwardsExpended"},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_not_public_returns_403_for_anon(self):
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

    @patch("audit.file_downloads.file_exists")
    def test_private_returns_403_for_anonymous(self, mock_file_exists):
        mock_file_exists.return_value = True

        sac, general = self._make_sac_and_general(is_public=False)

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": general.report_id,
                "file_type": "FederalAwardsExpended",
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    @patch("audit.file_downloads.file_exists")
    def test_private_returns_403_for_unpermissioned(self, mock_file_exists):
        mock_file_exists.return_value = True

        sac, general = self._make_sac_and_general(is_public=False)

        user = baker.make(User)

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": general.report_id,
                "file_type": "FederalAwardsExpended",
            },
        )

        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    @patch("audit.file_downloads.file_exists")
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
        file = baker.make(ExcelFile, sac=sac, form_section="FederalAwardsExpended")

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": general.report_id,
                "file_type": "FederalAwardsExpended",
            },
        )

        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(file.filename, response.url)


class SummaryViewTests(TestCase):
    def setUp(self):
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
        self.assertEquals(response.status_code, 200)

    def test_private_summary(self):
        """
        Anonymous requests for private audit summaries should return 403
        """
        baker.make(General, report_id="2022-12-GSAFAC-0000000001", is_public=False)
        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)
        self.assertEquals(response.status_code, 403)

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

        self.assertEquals(response.status_code, 200)

    def test_summary_context(self):
        """
        The summary context should include the same data that is in the models.
        Create a bunch of fake DB data under the same report_id. Then, check a few
        fields in the context for the summary page to verify that the fake data persists.
        """
        baker.make(General, report_id="2022-12-GSAFAC-0000000001", is_public=True)
        award = baker.make(FederalAward, report_id="2022-12-GSAFAC-0000000001")
        finding = baker.make(Finding, report_id="2022-12-GSAFAC-0000000001")
        finding_text = baker.make(FindingText, report_id="2022-12-GSAFAC-0000000001")
        cap_text = baker.make(CapText, report_id="2022-12-GSAFAC-0000000001")
        note = baker.make(Note, report_id="2022-12-GSAFAC-0000000001")

        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)
        self.assertEquals(
            response.context["data"]["Awards"][0]["additional_award_identification"],
            award.additional_award_identification,
        )
        self.assertEquals(
            response.context["data"]["Audit Findings"][0]["reference_number"],
            finding.reference_number,
        )
        self.assertEquals(
            response.context["data"]["Audit Findings Text"][0]["finding_ref_number"],
            finding_text.finding_ref_number,
        )
        self.assertEquals(
            response.context["data"]["Corrective Action Plan"][0][
                "contains_chart_or_table"
            ],
            cap_text.contains_chart_or_table,
        )
        self.assertEquals(
            response.context["data"]["Notes to SEFA"][0]["accounting_policies"],
            note.accounting_policies,
        )
