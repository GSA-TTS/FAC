from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.test.client import RequestFactory
from django.views import generic
from model_bakery import baker

from .mixins import (
    CertificationPermissionDenied,
    CertifyingAuditeeRequiredMixin,
    CertifyingAuditorRequiredMixin,
    SingleAuditChecklistAccessRequiredMixin,
)
from .models import Access, SingleAuditChecklist

User = get_user_model()


class SingleAuditChecklistAccessRequiredMixinTests(TestCase):
    class ViewStub(SingleAuditChecklistAccessRequiredMixin, generic.View):
        def get(self, request, *args, **kwargs):
            pass

    def test_missing_report_id_raises(self):
        request = RequestFactory().get("/")
        view = self.ViewStub()

        self.assertRaises(KeyError, view.dispatch, request)

    def test_nonexistent_sac_raises(self):
        request = RequestFactory().get("/")
        view = self.ViewStub()

        self.assertRaises(
            PermissionDenied, view.dispatch, request, report_id="not-a-real-report-id"
        )

    def test_no_access_raises(self):
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)

        request = RequestFactory().get("/")
        request.user = user

        view = self.ViewStub()
        self.assertRaises(
            PermissionDenied, view.dispatch, request, report_id=sac.report_id
        )

    def test_has_access(self):
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)
        baker.make(Access, sac=sac, user=user)

        request = RequestFactory().get("/")
        request.user = user

        view = self.ViewStub()
        view.dispatch(request, report_id=sac.report_id)


class CertifyingAuditeeRequiredMixinTests(TestCase):
    class ViewStub(CertifyingAuditeeRequiredMixin, generic.View):
        def get(self, request, *args, **kwargs):
            pass

    def test_missing_report_id_raises(self):
        request = RequestFactory().get("/")
        view = self.ViewStub()

        self.assertRaises(KeyError, view.dispatch, request)

    def test_nonexistent_sac_raises(self):
        request = RequestFactory().get("/")
        view = self.ViewStub()

        self.assertRaises(
            PermissionDenied, view.dispatch, request, report_id="not-a-real-report-id"
        )

    def test_no_access_raises(self):
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)

        request = RequestFactory().get("/")
        request.user = user
        view = self.ViewStub()

        self.assertRaises(
            PermissionDenied, view.dispatch, request, report_id=sac.report_id
        )

    def test_bad_role_raises_cert_perm_denied(self):
        role = "certifying_auditee_contact"
        bad_roles = [r[0] for r in Access.ROLES if r[0] != role]

        for bad_role in bad_roles:
            with self.subTest():
                user = baker.make(User)
                sac = baker.make(SingleAuditChecklist)
                baker.make(Access, sac=sac, user=user, role=bad_role)

                # create a second user with the appropriate role
                eligible_user = baker.make(User)
                baker.make(Access, sac=sac, user=eligible_user, role=role)

                request = RequestFactory().get("/")
                request.user = user

                try:
                    self.ViewStub().dispatch(request, report_id=sac.report_id)
                    msg = "expected dispatch to raise CertificationPermissionDenied"
                    self.fail(msg)
                except CertificationPermissionDenied as err:
                    self.assertEqual(len(err.eligible_users), 1)
                    self.assertEqual(err.eligible_users[0], eligible_user)
                except Exception as err:
                    msg = f"expected CertificationPermissionDenied, got {type(err)}"
                    self.fail(msg)

    def test_has_role(self):
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)

        baker.make(Access, sac=sac, user=user, role="certifying_auditee_contact")

        request = RequestFactory().get("/")
        request.user = user

        view = self.ViewStub()
        view.dispatch(request, report_id=sac.report_id)


class CertifyingAuditorRequiredMixinTests(TestCase):
    class ViewStub(CertifyingAuditorRequiredMixin, generic.View):
        def get(self, request, *args, **kwargs):
            pass

    def test_missing_report_id_raises(self):
        request = RequestFactory().get("/")
        view = self.ViewStub()

        self.assertRaises(KeyError, view.dispatch, request)

    def test_nonexistent_sac_raises(self):
        request = RequestFactory().get("/")
        view = self.ViewStub()

        self.assertRaises(
            PermissionDenied, view.dispatch, request, report_id="not-a-real-report-id"
        )

    def test_no_access_raises(self):
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)

        request = RequestFactory().get("/")
        request.user = user
        view = self.ViewStub()

        self.assertRaises(
            PermissionDenied, view.dispatch, request, report_id=sac.report_id
        )

    def test_bad_role_raises_cert_perm_denied(self):
        role = "certifying_auditor_contact"
        bad_roles = [r[0] for r in Access.ROLES if r[0] != role]

        for bad_role in bad_roles:
            with self.subTest():
                user = baker.make(User)
                sac = baker.make(SingleAuditChecklist)
                baker.make(Access, sac=sac, user=user, role=bad_role)

                # create a second user with the appropriate role
                eligible_user = baker.make(User)
                baker.make(Access, sac=sac, user=eligible_user, role=role)

                request = RequestFactory().get("/")
                request.user = user

                try:
                    self.ViewStub().dispatch(request, report_id=sac.report_id)
                    msg = "expected dispatch to raise CertificationPermissionDenied"
                    self.fail(msg)
                except CertificationPermissionDenied as err:
                    self.assertEqual(len(err.eligible_users), 1)
                    self.assertEqual(err.eligible_users[0], eligible_user)
                except Exception as err:
                    msg = f"expected CertificationPermissionDenied, got {type(err)}"
                    self.fail(msg)

    def test_has_role(self):
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)

        baker.make(Access, sac=sac, user=user, role="certifying_auditor_contact")

        request = RequestFactory().get("/")
        request.user = user

        view = self.ViewStub()
        view.dispatch(request, report_id=sac.report_id)
