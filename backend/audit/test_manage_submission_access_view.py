from django.contrib.auth.models import User as DjangoUser
from django.test import TestCase
from django.urls import reverse

from model_bakery import baker
from .models import (
    Access,
    DeletedAccess,
    SingleAuditChecklist,
    User,
    Audit,
)


def _make_test_users_by_email(emails: list[str]) -> list[DjangoUser]:
    return [baker.make(User, email=email) for email in emails]


def _make_access(sac: SingleAuditChecklist, role: str, user: DjangoUser) -> Access:
    return baker.make(Access, user=user, email=user.email, sac=sac, role=role)


def _make_user_sac_and_audit(**kwargs):
    user = baker.make(User)
    sac = baker.make(SingleAuditChecklist, **kwargs)
    audit = baker.make(Audit, version=0, **kwargs)
    return user, sac, audit


class ChangeOrAddRoleViewTests(TestCase):
    """
    GET and POST tests for adding editors to a submission.
    """

    role = "editor"
    view = "audit:ChangeOrAddRoleView"

    def test_basic_get(self):
        """
        A user should be able to access this page for a SAC they're associated with.
        """
        user, sac, audit = _make_user_sac_and_audit()
        baker.make(Access, user=user, sac=sac, audit=audit, role="editor")
        sac.general_information = {"auditee_uei": "YESIAMAREALUEI"}
        sac.save()

        self.client.force_login(user)
        url = reverse(self.view, kwargs={"report_id": sac.report_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("YESIAMAREALUEI", response.content.decode("UTF-8"))

    def test_basic_post(self):
        """
        Submitting the form with a new email address should create a new Access.
        """
        user = baker.make(User, email="adding_user@example.com")
        sac = baker.make(SingleAuditChecklist)
        audit = baker.make(
            Audit,
            version=0,
            audit={"general_information": {"auditee_uei": "YESIAMAREALUEI"}},
        )
        baker.make(Access, user=user, sac=sac, audit=audit, role="editor")
        sac.general_information = {"auditee_uei": "YESIAMAREALUEI"}
        sac.save()
        self.client.force_login(user)

        data = {
            "fullname": "The New Editor",
            "email": "neweditoruser@example.gov",
        }

        url = reverse(self.view, kwargs={"report_id": sac.report_id})
        response = self.client.post(url, data=data)
        self.assertEqual(302, response.status_code)

        newaccess = Access.objects.get(
            sac=sac, fullname=data["fullname"], email=data["email"]
        )
        self.assertEqual(self.role, newaccess.role)

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
        user, sac, _ = _make_user_sac_and_audit()

        self.client.force_login(user)
        response = self.client.post(
            reverse(self.view, kwargs={"report_id": sac.report_id})
        )

        self.assertEqual(response.status_code, 403)


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
        user, sac, audit = _make_user_sac_and_audit()
        baker.make(Access, user=user, sac=sac, role="editor")
        sac.general_information = {"auditee_uei": "YESIAMAREALUEI"}
        sac.save()
        audit.audit.update({"general_information": {"auditee_uei": "YESIAMAREALUEI"}})
        audit.save()

        current_cac = baker.make(Access, sac=sac, audit=audit, role=self.role)
        current_role = str(current_cac.get_friendly_role())

        self.client.force_login(user)
        url = reverse(self.view, kwargs={"report_id": sac.report_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("YESIAMAREALUEI", response.content.decode("UTF-8"))
        self.assertIn(current_cac.email, response.content.decode("UTF-8"))
        self.assertIn(current_role, response.content.decode("UTF-8"))

    def test_no_existing_role_get(self):
        """
        A user should be able to access this page for a SAC they're associated with
        even if there's no current assignment for the role.
        """
        user, sac, audit = _make_user_sac_and_audit()
        baker.make(Access, user=user, sac=sac, audit=audit, role="editor")
        sac.general_information = {"auditee_uei": "YESIAMAREALUEI"}
        sac.save()
        audit.audit.update({"general_information": {"auditee_uei": "YESIAMAREALUEI"}})
        audit.save()

        self.client.force_login(user)
        url = reverse(self.view, kwargs={"report_id": sac.report_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("YESIAMAREALUEI", response.content.decode("UTF-8"))
        self.assertIn("UNASSIGNED ROLE", response.content.decode("UTF-8"))

    def test_basic_post(self):
        """
        Submitting the form with a new email address should delete the existing
        Access, create a DeletedAccess, and create a new Access.
        """
        user = baker.make(User, email="removing_user@example.com")
        sac = baker.make(SingleAuditChecklist)
        audit = baker.make(Audit, version=0)
        baker.make(Access, user=user, sac=sac, audit=audit, role="editor")
        baker.make(
            Access,
            sac=sac,
            audit=audit,
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

    def test_no_existing_role_post(self):
        """
        Submitting the form with a new email address should delete the existing
        Access, create a DeletedAccess, and create a new Access.

        However, if we have no existing Access, we should still create a new Access.
        """
        user = baker.make(User, email="removing_user@example.com")
        sac = baker.make(SingleAuditChecklist)
        audit = baker.make(Audit, version=0)
        baker.make(Access, user=user, sac=sac, audit=audit, role="editor")
        baker.make(
            Access,
            sac=sac,
            audit=audit,
            role=self.other_role,
            email="contact@example.com",
        )
        sac.general_information = {"auditee_uei": "YESIAMAREALUEI"}
        sac.save()

        audit.audit.update({"general_information": {"auditee_uei": "YESIAMAREALUEI"}})
        audit.save()

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

    def test_bad_email_post(self):
        """
        Submitting an email address that's already in use for the other role should
        result in a 400 and returning to the form page.
        """
        new_email = "newcacuser@example.com"
        user = baker.make(User, email="removing_user@example.com")
        sac = baker.make(SingleAuditChecklist)
        audit = baker.make(Audit, version=0)
        baker.make(Access, audit=audit, user=user, sac=sac, role="editor")
        baker.make(Access, audit=audit, sac=sac, role=self.other_role, email=new_email)
        baker.make(Access, audit=audit, sac=sac, role=self.role)
        sac.general_information = {"auditee_uei": "YESIAMAREALUEI"}
        sac.save()
        audit.audit.update({"general_information": {"auditee_uei": "YESIAMAREALUEI"}})
        audit.save()
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
        user, sac, _ = _make_user_sac_and_audit()

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
