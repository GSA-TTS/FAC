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

    role = "certifying_auditor_contact"
    other_role = "certifying_auditee_contact"
    view = "audit:ChangeAuditorCertifyingOfficial"

    def test_basic_get(self):
        """
        A user should be able to access this page for a SAC they're associated with.
        """
        user, sac = _make_user_and_sac()
        baker.make(Access, user=user, sac=sac, role="editor")
        sac.general_information = {"auditee_uei": "YESIAMAREALUEI"}
        sac.save()
        current_cac = baker.make(Access, sac=sac, role=self.role)

        self.client.force_login(user)
        url = reverse(self.view, kwargs={"report_id": sac.report_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("YESIAMAREALUEI", response.content.decode("UTF-8"))
        self.assertIn(current_cac.email, response.content.decode("UTF-8"))

    def test_basic_post(self):
        """
        Submitting the form with a new email address should delete the existing
        Access, create a DeletedAccess, and create a new Access.
        """
        user = baker.make(User, email="removing_user@example.com")
        sac = baker.make(SingleAuditChecklist)
        baker.make(Access, user=user, sac=sac, role="editor")
        baker.make(
            Access,
            sac=sac,
            role=self.other_role,
            email="contact@example.com",
        )
        sac.general_information = {"auditee_uei": "YESIAMAREALUEI"}
        sac.save()
        current_cac = baker.make(Access, sac=sac, role=self.role)

        self.client.force_login(user)

        data = {
            "fullname": "The New CAC",
            "email": "newcacuser@example.com",
        }

        url = reverse(self.view, kwargs={"report_id": sac.report_id})
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)

        newaccess = Access.objects.get(
            sac=sac, fullname=data["fullname"], email=data["email"]
        )
        self.assertEqual(self.role, newaccess.role)
        oldaccess = DeletedAccess.objects.get(
            sac=sac,
            fullname=current_cac.fullname,
            email=current_cac.email,
        )
        self.assertEqual(self.role, oldaccess.role)

    def test_bad_email_post(self):
        """
        Submitting an email address that's already in use for the other role should
        result in a 400 and returning to the form page.
        """
        new_email = "newcacuser@example.com"
        user = baker.make(User, email="removing_user@example.com")
        sac = baker.make(SingleAuditChecklist)
        baker.make(Access, user=user, sac=sac, role="editor")
        baker.make(Access, sac=sac, role=self.other_role, email=new_email)
        baker.make(Access, sac=sac, role=self.role)
        sac.general_information = {"auditee_uei": "YESIAMAREALUEI"}
        sac.save()

        self.client.force_login(user)

        data = {"fullname": "The New CAC", "email": new_email}

        url = reverse(self.view, kwargs={"report_id": sac.report_id})
        response = self.client.post(url, data=data)
        self.assertEqual(400, response.status_code)

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


class ChangeAuditeeCertifyingOfficialViewTests(
    ChangeAuditorCertifyingOfficialViewTests
):
    """
    GET and POST tests for changing auditee certifying official.
    """

    role = "certifying_auditee_contact"
    other_role = "certifying_auditor_contact"
    view = "audit:ChangeAuditeeCertifyingOfficial"
