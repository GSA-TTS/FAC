from django.test import TestCase
from django.urls import reverse

from model_bakery import baker
from .models import (
    ACCESS_ROLES,
    Access,
    SingleAuditChecklist,
    User,
)


def _make_access_by_email(sac: SingleAuditChecklist, role: str, email: str) -> Access:
    return baker.make(Access, email=email, sac=sac, role=role)


def _make_user_and_sac(**kwargs):
    user = baker.make(User)
    sac = baker.make(SingleAuditChecklist, **kwargs)
    return user, sac


class ManageSubmissionViewTests(TestCase):
    """
    GET and POST tests for manage submission page.
    """

    view = "audit:ManageSubmission"

    def test_basic_get(self):
        """
        A user should be able to access this page for a SAC they're associated with.
        """
        user, sac = _make_user_and_sac()
        baker.make(
            Access,
            user=user,
            sac=sac,
            role="editor",
            email="arealemail@arealdomain.tld",
        )
        base_info = {
            "auditee_uei": "YESIAMAREALUEI",
            "auditee_name": "100% Human Organization",
            "auditee_fiscal_period_start": "1885-10-12",
            "auditee_fiscal_period_end": "1886-10-11",
        }
        rows = (
            ("certifying_auditee_contact", "auditee_cert_contact@example.com"),
            ("certifying_auditor_contact", "auditor_cert_contact@example.com"),
            ("editor", "someone@example.com"),
        )
        for row in rows:
            _make_access_by_email(sac, row[0], row[1])

        sac.general_information = base_info
        sac.save()
        self.client.force_login(user)
        url = reverse(self.view, kwargs={"report_id": sac.report_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        page = response.content.decode("UTF-8")
        self.assertIn("arealemail@arealdomain.tld", page)
        self.assertIn("In Progress", page)
        for value in base_info.values():
            self.assertIn(value, page)
        for _, email in rows:
            self.assertIn(email, page)
            # None of those users should exist:
            self.assertIn(f"{email}", page)
        for _, friendly_role in ACCESS_ROLES:
            self.assertIn(str(friendly_role), page)

    def test_login_required(self):
        """When an unauthenticated request is made"""

        response = self.client.get(
            reverse(
                self.view,
                kwargs={"report_id": "12345"},
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_bad_report_id_returns_403(self):
        """
        When a request is made for a malformed or nonexistent report_id,
        a 403 error should be returned
        """
        user = baker.make(User)

        self.client.force_login(user)

        response = self.client.get(
            reverse(self.view, kwargs={"report_id": "this is not a report id"})
        )

        self.assertEqual(response.status_code, 403)

    def test_inaccessible_audit_returns_403(self):
        """When a request is made for an audit that is inaccessible for this user, a 403 error should be returned"""
        user, sac = _make_user_and_sac()

        self.client.force_login(user)
        response = self.client.post(
            reverse(self.view, kwargs={"report_id": sac.report_id})
        )

        self.assertEqual(response.status_code, 403)
