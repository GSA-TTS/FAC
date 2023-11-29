from django.contrib.auth.models import User as DjangoUser
from django.test import TestCase
from django.urls import reverse

from model_bakery import baker
from .models import (
    Access,
    DeletedAccess,
    SingleAuditChecklist,
    User,
)


def _make_test_users_by_email(emails: list[str]) -> list[DjangoUser]:
    return [baker.make(User, email=email) for email in emails]


def _make_access(sac: SingleAuditChecklist, role: str, user: DjangoUser) -> Access:
    return baker.make(Access, user=user, email=user.email, sac=sac, role=role)


def _make_user_and_sac(**kwargs):
    user = baker.make(User)
    sac = baker.make(SingleAuditChecklist, **kwargs)
    return user, sac


class ChangeAuditorCertifyingOfficialViewTests(TestCase):
    """
    GET and POST tests for changing auditor certifying official.
    """

    def test_basic_get(self):
        """
        A user should be able to access this page for a SAC they're associated with.
        """
        user, sac = _make_user_and_sac()
        baker.make(Access, user=user, sac=sac, role="editor")
        sac.general_information = {"auditee_uei": "YESIAMAREALUEI"}
        sac.save()
        current_cac = baker.make(Access, sac=sac, role="certifying_auditor_contact")

        self.client.force_login(user)
        response = self.client.get(
            reverse(
                "audit:ChangeAuditorCertifyingOfficial",
                kwargs={"report_id": sac.report_id},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("YESIAMAREALUEI", response.content.decode("UTF-8"))
        self.assertIn(current_cac.email, response.content.decode("UTF-8"))

    def test_basic_post(self):
        user = baker.make(User, email="removing_user@example.com")
        sac = baker.make(SingleAuditChecklist)
        baker.make(Access, user=user, sac=sac, role="editor")
        sac.general_information = {"auditee_uei": "YESIAMAREALUEI"}
        sac.save()
        current_cac = baker.make(Access, sac=sac, role="certifying_auditor_contact")

        self.client.force_login(user)

        data = {
            "fullname": "The New CAC",
            "email": "newcacuser@example.com",
        }

        url = reverse(
            "audit:ChangeAuditorCertifyingOfficial", kwargs={"report_id": sac.report_id}
        )
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)

        newaccess = Access.objects.get(
            sac=sac, fullname=data["fullname"], email=data["email"]
        )
        self.assertEqual("certifying_auditor_contact", newaccess.role)
        oldaccess = DeletedAccess.objects.get(
            sac=sac,
            fullname=current_cac.fullname,
            email=current_cac.email,
        )
        self.assertEqual("certifying_auditor_contact", oldaccess.role)

    def test_login_required(self):
        """When an unauthenticated request is made"""

        response = self.client.get(
            reverse(
                "audit:ChangeAuditorCertifyingOfficial",
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
            reverse(
                "audit:ChangeAuditorCertifyingOfficial",
                kwargs={"report_id": "this is not a report id"},
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_inaccessible_audit_returns_403(self):
        """When a request is made for an audit that is inaccessible for this user, a 403 error should be returned"""
        user, sac = _make_user_and_sac()

        self.client.force_login(user)
        response = self.client.post(
            reverse(
                "audit:ChangeAuditorCertifyingOfficial",
                kwargs={"report_id": sac.report_id},
            )
        )

        self.assertEqual(response.status_code, 403)
