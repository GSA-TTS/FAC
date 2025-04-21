from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from model_bakery import baker
from .models import ACCESS_ROLES, Access, Audit


def _make_access_by_email(audit: Audit, role: str, email: str) -> Access:
    return baker.make(Access, email=email, audit=audit, role=role)


def _make_user_and_audit():
    user = baker.make(User)
    audit = baker.make(Audit, version=0)
    return user, audit


class ManageSubmissionViewTests(TestCase):
    """
    GET and POST tests for manage submission page.
    """

    view = "audit:ManageSubmission"

    def test_basic_get(self):
        """
        A user should be able to access this page for a SAC they're associated with.
        """
        user, audit = _make_user_and_audit()
        baker.make(
            Access,
            user=user,
            audit=audit,
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
            _make_access_by_email(audit, row[0], row[1])

        audit.audit.update({"general_information": base_info})
        audit.save()
        self.client.force_login(user)
        url = reverse(self.view, kwargs={"report_id": audit.report_id})
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

        self.assertTemplateUsed(response, "home.html")
        self.assertTrue(response.context["session_expired"])

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
        user, audit = _make_user_and_audit()

        self.client.force_login(user)
        response = self.client.post(
            reverse(self.view, kwargs={"report_id": audit.report_id})
        )

        self.assertEqual(response.status_code, 403)
