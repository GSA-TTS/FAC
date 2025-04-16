import io
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from audit.models import (
    ExcelFile,
    Audit,
    SingleAuditReportFile,
)

from audit.fixtures.excel import FORM_SECTIONS
from audit.models.constants import STATUS, ORGANIZATION_TYPE
from audit.models.utils import generate_sac_report_id
from dissemination.models.one_time_access import OneTimeAccess
from dissemination.test_search import generate_valid_audit_for_search
from dissemination.views.utils import to_date

from users.models import Permission, UserPermission

from model_bakery import baker
from unittest.mock import patch

from datetime import timedelta
from uuid import uuid4

User = get_user_model()


def _make_audit(is_public=True, submission_status=STATUS.DISSEMINATED):
    audit_data = {
        "is_public": is_public,
    }
    audit = baker.make(
        Audit,
        version=0,
        audit=audit_data,
        submission_status=submission_status,
        report_id=generate_sac_report_id(Audit.objects.count(), "2023-12-31"),
    )

    return audit


def _make_multiple_audits(
    quantity=1,
    is_public=True,
    overrides=None,
    report_id=None,
    submission_status=STATUS.DISSEMINATED,
):
    audits = []
    for i in range(quantity):
        audits.append(
            generate_valid_audit_for_search(
                is_public=is_public,
                overrides=overrides,
                submission_status=submission_status,
                report_id=report_id,
            )
        )

    return audits


class PdfDownloadViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_bad_report_id_returns_404(self):
        url = reverse("dissemination:PdfDownload", kwargs={"report_id": "not-real"})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_not_public_returns_403(self):
        audit = _make_audit(is_public=False)

        url = reverse(
            "dissemination:PdfDownload", kwargs={"report_id": audit.report_id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_no_file_returns_404(self):
        audit = _make_audit()

        url = reverse(
            "dissemination:PdfDownload", kwargs={"report_id": audit.report_id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_not_disseminated_404(self):
        audit = _make_audit(submission_status=STATUS.IN_PROGRESS)

        url = reverse(
            "dissemination:PdfDownload", kwargs={"report_id": audit.report_id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    @patch("dissemination.file_downloads.file_exists")
    def test_file_exists_returns_302(self, mock_file_exists):
        mock_file_exists.return_value = True

        audit = _make_audit(submission_status=STATUS.IN_PROGRESS)
        file = baker.make(SingleAuditReportFile, audit=audit)
        audit.submission_status = STATUS.DISSEMINATED
        audit.save()

        url = reverse(
            "dissemination:PdfDownload", kwargs={"report_id": audit.report_id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(file.filename, response.url)

    @patch("dissemination.file_downloads.file_exists")
    def test_private_returns_403_for_anonymous(self, mock_file_exists):
        mock_file_exists.return_value = True

        audit = _make_audit(is_public=False)

        url = reverse(
            "dissemination:PdfDownload", kwargs={"report_id": audit.report_id}
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    @patch("dissemination.file_downloads.file_exists")
    def test_private_returns_403_for_unpermissioned(self, mock_file_exists):
        mock_file_exists.return_value = True

        audit = _make_audit(is_public=False)

        user = baker.make(User)

        url = reverse(
            "dissemination:PdfDownload", kwargs={"report_id": audit.report_id}
        )

        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    @patch("dissemination.file_downloads.file_exists")
    def test_private_returns_302_for_permissioned(self, mock_file_exists):
        mock_file_exists.return_value = True

        audit = _make_audit(is_public=False, submission_status=STATUS.IN_PROGRESS)

        user = baker.make(User)
        permission = Permission.objects.get(slug=Permission.PermissionType.READ_TRIBAL)
        baker.make(
            UserPermission,
            email=user.email,
            user=user,
            permission=permission,
        )
        file = baker.make(SingleAuditReportFile, audit=audit)
        audit.submission_status = STATUS.DISSEMINATED
        audit.save()

        url = reverse(
            "dissemination:PdfDownload", kwargs={"report_id": audit.report_id}
        )

        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(file.filename, response.url)


class SearchViewTests(TestCase):
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

        # If there are results, we'll see "results in x seconds" somewhere.
        self.assertNotContains(response, "results in")

    def test_anonymous_returns_private_and_public(self):
        """Anonymous users should see all reports (public and private included)."""
        public = _make_multiple_audits(quantity=5)
        private = _make_multiple_audits(quantity=5, is_public=False)

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
        public = _make_multiple_audits(quantity=5)
        private = _make_multiple_audits(quantity=5, is_public=False)

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
        public = _make_multiple_audits(quantity=5)
        private = _make_multiple_audits(quantity=5, is_public=False)

        response = self.perm_client.post(self._search_url(), {})

        # 1-10 of <strong>10</strong> results in x seconds.
        self.assertContains(response, "<strong>10</strong>")

        # all of the public reports should show up on the page
        for p in public:
            self.assertContains(response, p.report_id)

        # all of the private reports should show up on the page
        for p in private:
            self.assertContains(response, p.report_id)


class PublicDataDownloadViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.mock_file_path = "public-data/historic/2022.zip"

    @patch("dissemination.file_downloads.file_exists")
    def test_no_file_returns_404(self, mock_file_exists):
        """
        Given a relative path to a file that doesn't exist
        When a request is sent to the public data download URL
        Then the response should be 404
        """
        mock_file_exists.return_value = False
        url = reverse(
            "dissemination:PublicDataDownload",
            kwargs={"relative_path": self.mock_file_path},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    @patch("dissemination.file_downloads.file_exists")
    def test_exisiting_file_returns_redirect(self, mock_file_exists):
        """
        Given a relative path to a file that exists
        When a request is sent to the public data download URL
        Then the response should be a redirect to the file download
        """
        mock_file_exists.return_value = True
        url = reverse(
            "dissemination:PublicDataDownload",
            kwargs={"relative_path": self.mock_file_path},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(self.mock_file_path, response.url)


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

        audit = _make_audit(submission_status=STATUS.IN_PROGRESS)
        baker.make(SingleAuditReportFile, audit=audit)
        audit.submission_status = STATUS.DISSEMINATED
        audit.save()

        ota = baker.make(OneTimeAccess, uuid=uuid, report_id=audit.report_id)

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

        report_id = generate_sac_report_id(count=100_000, end_date="2024-01-31")
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

        audit = _make_audit()
        baker.make(OneTimeAccess, uuid=uuid, report_id=audit.report_id)

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

        audit = _make_audit(submission_status=STATUS.IN_PROGRESS)
        baker.make(SingleAuditReportFile, audit=audit)
        audit.submission_status = STATUS.DISSEMINATED
        audit.save()

        baker.make(OneTimeAccess, uuid=uuid, report_id=audit.report_id)

        url = reverse("dissemination:OtaPdfDownload", kwargs={"uuid": uuid})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(audit.report_id, response.url)

        response_2 = self.client.get(url)

        self.assertEqual(response_2.status_code, 404)


class XlsxDownloadViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_bad_report_id_returns_404(self):
        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={"report_id": "not-real", "file_type": FORM_SECTIONS.FEDERAL_AWARDS},
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    def test_not_public_returns_403_for_anon(self):
        audit = _make_audit(is_public=False)

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": audit.report_id,
                "file_type": FORM_SECTIONS.FEDERAL_AWARDS,
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    def test_no_file_returns_404(self):
        audit = _make_audit()

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": audit.report_id,
                "file_type": FORM_SECTIONS.FEDERAL_AWARDS,
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)

    @patch("dissemination.file_downloads.file_exists")
    def test_file_exists_returns_302(self, mock_file_exists):
        mock_file_exists.return_value = True

        audit = _make_audit(submission_status=STATUS.IN_PROGRESS)
        file = baker.make(
            ExcelFile, audit=audit, form_section=FORM_SECTIONS.FEDERAL_AWARDS
        )
        audit.submission_status = STATUS.DISSEMINATED
        audit.save()

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": audit.report_id,
                "file_type": FORM_SECTIONS.FEDERAL_AWARDS,
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(file.filename, response.url)

    @patch("dissemination.file_downloads.file_exists")
    def test_private_returns_403_for_anonymous(self, mock_file_exists):
        mock_file_exists.return_value = True

        audit = _make_audit(is_public=False)

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": audit.report_id,
                "file_type": FORM_SECTIONS.FEDERAL_AWARDS,
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    @patch("dissemination.file_downloads.file_exists")
    def test_private_returns_403_for_unpermissioned(self, mock_file_exists):
        mock_file_exists.return_value = True

        audit = _make_audit(is_public=False)

        user = baker.make(User)

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": audit.report_id,
                "file_type": FORM_SECTIONS.FEDERAL_AWARDS,
            },
        )

        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)

    @patch("dissemination.file_downloads.file_exists")
    def test_private_returns_302_for_permissioned(self, mock_file_exists):
        mock_file_exists.return_value = True

        audit = _make_audit(is_public=False, submission_status=STATUS.IN_PROGRESS)

        user = baker.make(User)
        permission = Permission.objects.get(slug=Permission.PermissionType.READ_TRIBAL)
        baker.make(
            UserPermission,
            email=user.email,
            user=user,
            permission=permission,
        )
        file = baker.make(
            ExcelFile, audit=audit, form_section=FORM_SECTIONS.FEDERAL_AWARDS
        )
        audit.submission_status = STATUS.DISSEMINATED
        audit.save()

        url = reverse(
            "dissemination:XlsxDownload",
            kwargs={
                "report_id": audit.report_id,
                "file_type": FORM_SECTIONS.FEDERAL_AWARDS,
            },
        )

        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertIn(file.filename, response.url)


class SummaryViewTests(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_public_summary(self):
        """
        A public audit should have a viewable summary, and returns 200.
        """
        _make_multiple_audits(quantity=1, report_id="2022-12-GSAFAC-0000000001")

        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_private_summary(self):
        """
        Anonymous requests for private audit summaries should return 200
        """
        _make_multiple_audits(
            quantity=1, report_id="2022-12-GSAFAC-0000000001", is_public=False
        )
        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_permissioned_private_summary(self):
        """
        Permissioned requests for private audit summaries should return 200
        """
        audit = _make_multiple_audits(quantity=1, is_public=False)
        user = baker.make(User)

        permission = Permission.objects.get(slug=Permission.PermissionType.READ_TRIBAL)
        baker.make(UserPermission, user=user, email=user.email, permission=permission)

        url = reverse("dissemination:Summary", kwargs={"report_id": audit[0].report_id})

        self.client.force_login(user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)

    def test_summary_header_context(self):
        """
        The summary context should include the same data that is in the models.
        Create a bunch of fake DB data under the same report_id. Then, check a few
        fields in the context for the summary page to verify that the fake data persists.
        """
        audit = _make_multiple_audits(
            quantity=1, report_id="2022-12-GSAFAC-0000000001"
        )[0]

        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)
        header = response.context.get("header")

        self.assertEqual(header["auditee_name"], audit.auditee_name)
        self.assertEqual(header["auditee_uei"], audit.auditee_uei)
        self.assertEqual(header["fac_accepted_date"], to_date(audit.fac_accepted_date))
        self.assertEqual(header["report_id"], audit.report_id)
        self.assertEqual(
            header["fy_start_date"],
            to_date(audit.audit["general_information"]["auditee_fiscal_period_start"]),
        )
        self.assertEqual(
            header["fy_end_date"],
            to_date(audit.audit["general_information"]["auditee_fiscal_period_end"]),
        )

    def test_summary_auditee_info_context(self):
        audit = _make_multiple_audits(
            quantity=1, report_id="2022-12-GSAFAC-0000000001"
        )[0]

        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)
        auditee_info = response.context.get("auditee_info")

        self.assertEqual(
            auditee_info["auditee_contact_name"],
            audit.audit["general_information"]["auditee_contact_name"],
        )
        self.assertEqual(
            auditee_info["auditee_contact_title"],
            audit.audit["general_information"]["auditee_contact_title"],
        )
        self.assertEqual(
            auditee_info["auditee_email"],
            audit.audit["general_information"]["auditee_email"],
        )
        self.assertEqual(
            auditee_info["auditee_phone"],
            audit.audit["general_information"]["auditee_phone"],
        )
        self.assertEqual(
            auditee_info["auditee_address_line_1"],
            audit.audit["general_information"]["auditee_address_line_1"],
        )
        self.assertEqual(
            auditee_info["auditee_city"],
            audit.audit["general_information"]["auditee_city"],
        )
        self.assertEqual(
            auditee_info["auditee_state"],
            audit.audit["general_information"]["auditee_state"],
        )
        self.assertEqual(
            auditee_info["auditee_zip"],
            audit.audit["general_information"]["auditee_zip"],
        )
        self.assertEqual(auditee_info["ein"], audit.audit["general_information"]["ein"])
        self.assertEqual(
            auditee_info["auditee_certify_name"],
            audit.audit["auditee_certification"]["auditee_signature"]["auditee_name"],
        )
        self.assertEqual(
            auditee_info["auditee_certify_title"],
            audit.audit["auditee_certification"]["auditee_signature"]["auditee_title"],
        )

    def test_summary_auditor_info_context(self):
        audit = _make_multiple_audits(
            quantity=1, report_id="2022-12-GSAFAC-0000000001"
        )[0]

        url = reverse(
            "dissemination:Summary", kwargs={"report_id": "2022-12-GSAFAC-0000000001"}
        )

        response = self.client.get(url)
        auditor_info = response.context.get("auditor_info")

        self.assertEqual(
            auditor_info["auditor_contact_name"],
            audit.audit["general_information"]["auditor_contact_name"],
        )
        self.assertEqual(
            auditor_info["auditor_contact_title"],
            audit.audit["general_information"]["auditor_contact_title"],
        )
        self.assertEqual(
            auditor_info["auditor_email"],
            audit.audit["general_information"]["auditor_email"],
        )
        self.assertEqual(
            auditor_info["auditor_phone"],
            audit.audit["general_information"]["auditor_phone"],
        )
        self.assertEqual(
            auditor_info["auditor_address_line_1"],
            audit.audit["general_information"]["auditor_address_line_1"],
        )
        self.assertEqual(
            auditor_info["auditor_city"],
            audit.audit["general_information"]["auditor_city"],
        )
        self.assertEqual(
            auditor_info["auditor_state"],
            audit.audit["general_information"]["auditor_state"],
        )
        self.assertEqual(
            auditor_info["auditor_zip"],
            audit.audit["general_information"]["auditor_zip"],
        )

    def test_summary_additional_context(self):
        """Tests the "additional" fields: i.e. Additional UEIs, Additional EINs, Secondary Auditors"""

        # The extra saves are required so we don't accidentally overwrite all of
        # general information, and we can only update some fields if the status is in-progress
        audit_with_extras = _make_multiple_audits(
            overrides={
                "additional_eins": ["ADDITIONAL_EIN"],
                "additional_ueis": ["ADDITIONAL_UEI"],
            },
            submission_status=STATUS.IN_PROGRESS,
        )[0]
        audit_with_extras.audit["general_information"][
            "secondary_auditors_exist"
        ] = True
        audit_with_extras.save()
        audit_with_extras.submission_status = STATUS.DISSEMINATED
        audit_with_extras.save()

        url_with_extras = reverse(
            "dissemination:Summary", kwargs={"report_id": audit_with_extras.report_id}
        )

        response_with_extras = self.client.get(url_with_extras)
        auditor_info_with_extras = response_with_extras.context.get("auditor_info")
        auditee_info_with_extras = response_with_extras.context.get("auditee_info")

        self.assertEqual("Y", auditor_info_with_extras["has_secondary_auditors"])
        self.assertEqual("Y", auditee_info_with_extras["additional_eins"])
        self.assertEqual("Y", auditee_info_with_extras["additional_ueis"])

        # The extra saves are required so we don't accidentally overwrite all of
        # general information, and we can only update some fields if the status is in-progress
        audit_no_extras = _make_multiple_audits(
            overrides={"additional_eins": [], "additional_ueis": []},
            submission_status=STATUS.IN_PROGRESS,
        )[0]
        audit_no_extras.audit["general_information"]["secondary_auditors_exist"] = False
        audit_no_extras.save()
        audit_no_extras.submission_status = STATUS.DISSEMINATED
        audit_no_extras.save()

        url_no_extras = reverse(
            "dissemination:Summary", kwargs={"report_id": audit_no_extras.report_id}
        )

        response_no_extras = self.client.get(url_no_extras)
        auditor_info_no_extras = response_no_extras.context.get("auditor_info")
        auditee_info_no_extras = response_no_extras.context.get("auditee_info")

        self.assertEqual("N", auditor_info_no_extras["has_secondary_auditors"])
        self.assertEqual("N", auditee_info_no_extras["additional_eins"])
        self.assertEqual("N", auditee_info_no_extras["additional_ueis"])

    def test_public_findings_notes_context(self):
        """
        Test that the Audit Findings in the context only include distinct findings
        based on the `reference_number` for a given report_id.
        """
        audit = _make_multiple_audits()[0]

        url = reverse("dissemination:Summary", kwargs={"report_id": audit.report_id})

        response = self.client.get(url)
        summary = response.context.get("summary")
        self.assertEqual(
            summary["number_of_federal_awards"],
            len(audit.audit["federal_awards"].get("awards", [])),
        )
        self.assertEqual(
            summary["number_of_findings"],
            audit.audit["search_indexes"].get("unique_audit_findings_count", 0),
        )
        self.assertEqual(
            summary["total_amount_expended"],
            audit.audit["federal_awards"]["total_amount_expended"],
        )

        # These fields are based on is public
        notes_count = (
            max(
                len(
                    audit.audit.get("notes_to_sefa", {}).get(
                        "notes_to_sefa_entries", []
                    )
                ),
                1,
            )
            if audit.audit["notes_to_sefa"]
            else 0
        )
        self.assertEqual(summary["number_of_notes"], notes_count)
        self.assertEqual(
            summary["number_of_findings_text"],
            len(audit.audit.get("findings_text", [])),
        )
        self.assertEqual(
            summary["number_of_caps"],
            len(audit.audit.get("corrective_action_plan", [])),
        )

    def test_private_findings_notes_context(self):
        """
        Test that the Audit Findings in the context only include distinct findings
        based on the `reference_number` for a given report_id.
        """
        audit = _make_multiple_audits(submission_status=STATUS.IN_PROGRESS)[0]
        # The extra saves are required so we don't accidentally overwrite all of
        # general information, and we can only update some fields if the status is in-progress
        audit.audit["general_information"][
            "user_provided_organization_type"
        ] = ORGANIZATION_TYPE.TRIBAL
        audit.audit["is_public"] = False
        audit.save()
        audit.submission_status = STATUS.DISSEMINATED
        audit.save()

        url = reverse("dissemination:Summary", kwargs={"report_id": audit.report_id})

        response = self.client.get(url)
        summary = response.context.get("summary")
        self.assertEqual(
            summary["number_of_federal_awards"],
            len(audit.audit["federal_awards"].get("awards", [])),
        )
        self.assertEqual(
            summary["number_of_findings"],
            audit.audit["search_indexes"].get("unique_audit_findings_count", 0),
        )
        self.assertEqual(
            summary["total_amount_expended"],
            audit.audit["federal_awards"]["total_amount_expended"],
        )

        # These fields are based on is public

        self.assertEqual(summary["number_of_notes"], "N/A")
        self.assertEqual(summary["number_of_findings_text"], "N/A")
        self.assertEqual(summary["number_of_caps"], "N/A")

    def test_sac_download_available(self):
        """
        Ensures allow_download is True when a submission's SF-SAC is downloadable
        """
        audit = _make_multiple_audits()[0]
        url = reverse("dissemination:Summary", kwargs={"report_id": audit.report_id})

        response = self.client.get(url)
        self.assertEqual(response.context.get("allow_download"), True)


# TODO: Patching not working for some reason
class SummaryReportDownloadViewTests(TestCase):
    def setUp(self):
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

    def _summary_report_url(self):
        return reverse("dissemination:MultipleSummaryReportDownload")

    def _mock_filename(self):
        return "some-report-name.xlsx", None

    def _mock_download_url(self):
        return "http://example.com/gsa-fac-private-s3/temp/some-report-name.xlsx"

    def test_bad_search_returns_400(self):
        """
        Submitting a form with bad parameters should throw a BadRequest.
        """
        response = self.anon_client.post(
            self._summary_report_url(), {"start_date": "Not a date"}
        )
        self.assertEqual(response.status_code, 400)

    def test_empty_results_returns_404(self):
        """
        Searches with no results should return a 404, not an empty excel file.
        """
        _make_multiple_audits(
            is_public=False, overrides={"general_information": {"uei": "123456789012"}}
        )

        response = self.anon_client.post(
            self._summary_report_url(), {"uei_or_ein": "NotTheOther1"}
        )
        self.assertEqual(response.status_code, 404)

    @patch("dissemination.views.download.generate_audit_summary_report")
    def test_authorized_user_with_private_data(
        self, mock_generate_audit_summary_report
    ):
        """Test that an authorized user can access private data."""
        mock_filename = "mocked-report.xlsx"
        mock_workbook_bytes = io.BytesIO(b"fake file content")
        mock_generate_audit_summary_report.return_value = (
            mock_filename,
            mock_workbook_bytes,
        )

        _make_audit(is_public=False)

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

    @patch("dissemination.views.download.generate_audit_summary_report")
    def test_unauthorized_user_with_private_data(
        self, mock_prepare_workbook_for_download
    ):
        """Test that an unauthorized user can still receive a file, but without private data."""
        mock_filename = "mocked-report.xlsx"
        mock_workbook_bytes = io.BytesIO(b"fake file content")
        mock_prepare_workbook_for_download.return_value = (
            mock_filename,
            mock_workbook_bytes,
        )

        _make_audit(is_public=False)

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

    @patch("dissemination.views.download.generate_audit_summary_report")
    def test_authorized_user_with_public_data(self, mock_prepare_workbook_for_download):
        """Test that an authorized user can access public data."""
        mock_filename = "mocked-report.xlsx"
        mock_workbook_bytes = io.BytesIO(b"fake file content")
        mock_prepare_workbook_for_download.return_value = (
            mock_filename,
            mock_workbook_bytes,
        )

        _make_audit()

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

    @patch("dissemination.views.download.generate_audit_summary_report")
    def test_unauthorized_user_with_public_data(
        self, mock_prepare_workbook_for_download
    ):
        """Test that an unauthorized user can access public data."""
        mock_filename = "mocked-report.xlsx"
        mock_workbook_bytes = io.BytesIO(b"fake file content")
        mock_prepare_workbook_for_download.return_value = (
            mock_filename,
            mock_workbook_bytes,
        )

        _make_audit()

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

    @patch("dissemination.views.download.generate_audit_summary_report")
    def test_empty_search_params_returns_file(self, mock_prepare_workbook_for_download):
        """
        File should be generated on empty search parameters ("search all").
        """
        mock_filename = "mocked-report.xlsx"
        mock_workbook_bytes = io.BytesIO(b"fake file content")
        mock_prepare_workbook_for_download.return_value = (
            mock_filename,
            mock_workbook_bytes,
        )

        _make_audit()

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

    @patch("dissemination.views.download.generate_audit_summary_report")
    def test_many_results_returns_file(self, mock_prepare_workbook_for_download):
        """
        File should still be generated if there are above SUMMARY_REPORT_DOWNLOAD_LIMIT total results.
        """
        mock_filename = "mocked-report.xlsx"
        mock_workbook_bytes = io.BytesIO(b"fake file content")
        mock_prepare_workbook_for_download.return_value = (
            mock_filename,
            mock_workbook_bytes,
        )

        _make_multiple_audits(quantity=4)

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

    @patch("dissemination.views.search.run_search")
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

    @patch("dissemination.views.search.run_search")
    def test_advanced_search_post_page_zero(self, mock_run_search):
        """Ensure page resets to 1 when the requested page is zero"""
        mock_run_search.return_value.count.return_value = 5

        invalid_data = self.valid_post_data.copy()
        invalid_data["page"] = "0"

        response = self.client.post(self.advanced_search_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page"], 1)  # Should reset to 1

    @patch("dissemination.views.search.run_search")
    def test_advanced_search_post_page_empty(self, mock_run_search):
        """Ensure page defaults to 1 when no page is provided"""
        mock_run_search.return_value.count.return_value = 5

        invalid_data = self.valid_post_data.copy()
        invalid_data["page"] = ""

        response = self.client.post(self.advanced_search_url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page"], 1)  # Should default to 1

    @patch("dissemination.views.search.run_search")
    def test_advanced_search_post_valid_page(self, mock_run_search):
        """Ensure valid page number remains unchanged"""
        mock_run_search.return_value.count.return_value = 20  # Multiple pages exist

        valid_data = self.valid_post_data.copy()
        valid_data["page"] = "2"  # Valid page

        response = self.client.post(self.advanced_search_url, valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["page"], 2)  # Should remain 2
