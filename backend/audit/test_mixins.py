from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.test.client import RequestFactory
from django.views import generic
from model_bakery import baker

from .mixins import CertificationPermissionDenied, CertifyingAuditeeRequiredMixin, CertifyingAuditorRequiredMixin, SingleAuditChecklistAccessRequiredMixin
from .models import Access, SingleAuditChecklist

User = get_user_model()

class SingleAuditChecklistAccessRequiredMixinTests(TestCase):
    class ViewStub(SingleAuditChecklistAccessRequiredMixin, generic.View):
        def get(self, request, *args, **kwargs):
            pass

    def test_missing_report_id_raises(self):
        factory = RequestFactory()
        request = factory.get("/")

        view = self.ViewStub()
        self.assertRaises(KeyError, view.dispatch, request)

    def test_nonexistent_sac_raises(self):
        factory = RequestFactory()
        request = factory.get("/")

        view = self.ViewStub()
        self.assertRaises(PermissionDenied, view.dispatch, request, report_id="not-a-real-report-id")

    def test_no_access_raises(self):
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)

        factory = RequestFactory()
        request = factory.get("/")

        request.user = user

        view = self.ViewStub()
        self.assertRaises(PermissionDenied, view.dispatch, request, report_id=sac.report_id)

    def test_has_access(self):
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)
        baker.make(Access, sac=sac, user=user)

        factory = RequestFactory()
        request = factory.get("/")

        request.user = user

        view = self.ViewStub()
        view.dispatch(request, report_id=sac.report_id)


class CertifyingAuditeeRequiredMixinTests(TestCase):
    class ViewStub(CertifyingAuditeeRequiredMixin, generic.View):
        def get(self, request, *args, **kwargs):
            pass

    def test_missing_report_id_raises(self):
        factory = RequestFactory()
        request = factory.get("/")

        view = self.ViewStub()
        self.assertRaises(KeyError, view.dispatch, request)


    def test_nonexistent_sac_raises(self):
        factory = RequestFactory()
        request = factory.get("/")

        view = self.ViewStub()
        self.assertRaises(PermissionDenied, view.dispatch, request, report_id="not-a-real-report-id")

    def test_no_access_raises(self):
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)

        factory = RequestFactory()
        request = factory.get("/")

        request.user = user

        view = self.ViewStub()
        self.assertRaises(PermissionDenied, view.dispatch, request, report_id=sac.report_id)

    def test_bad_role_raises_cert_perm_denied(self):
        bad_roles = [r[0] for r in Access.ROLES if r[0] != "certifying_auditee_contact"]

        for bad_role in bad_roles:
            with self.subTest():
                user = baker.make(User)
                sac = baker.make(SingleAuditChecklist)
                baker.make(Access, sac=sac, user=user, role=bad_role)

                # create a second user with the appropriate role
                eligible_user = baker.make(User)
                baker.make(Access, sac=sac, user=eligible_user, role="certifying_auditee_contact")

                factory = RequestFactory()
                request = factory.get("/")

                request.user = user

                view = self.ViewStub()

                try:
                    view.dispatch(request, report_id=sac.report_id)
                    self.fail("expected dispatch to raise CertificationPermissionDenied")
                except CertificationPermissionDenied as e:
                    self.assertEqual(len(e.eligible_users), 1)
                    self.assertEqual(e.eligible_users[0], eligible_user)
                except Exception as e:
                    self.fail(f"expected CertificationPermissionDenied, got {type(e)}")

    def test_has_role(self):
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)

        baker.make(Access, sac=sac, user=user, role="certifying_auditee_contact")

        factory = RequestFactory()
        request = factory.get("/")

        request.user = user

        view = self.ViewStub()
        view.dispatch(request, report_id=sac.report_id)


class CertifyingAuditorRequiredMixinTests(TestCase):
    class ViewStub(CertifyingAuditorRequiredMixin, generic.View):
        def get(self, request, *args, **kwargs):
            pass

    def test_missing_report_id_raises(self):
        factory = RequestFactory()
        request = factory.get("/")

        view = self.ViewStub()
        self.assertRaises(KeyError, view.dispatch, request)

    def test_nonexistent_sac_raises(self):
        factory = RequestFactory()
        request = factory.get("/")

        view = self.ViewStub()
        self.assertRaises(PermissionDenied, view.dispatch, request, report_id="not-a-real-report-id")

    def test_no_access_raises(self):
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)

        factory = RequestFactory()
        request = factory.get("/")

        request.user = user

        view = self.ViewStub()
        self.assertRaises(PermissionDenied, view.dispatch, request, report_id=sac.report_id)

    def test_bad_role_raises_cert_perm_denied(self):
        bad_roles = [r[0] for r in Access.ROLES if r[0] != "certifying_auditor_contact"]

        for bad_role in bad_roles:
            with self.subTest():
                user = baker.make(User)
                sac = baker.make(SingleAuditChecklist)
                baker.make(Access, sac=sac, user=user, role=bad_role)

                factory = RequestFactory()
                request = factory.get("/")

                request.user = user

                view = self.ViewStub()

                self.assertRaises(CertificationPermissionDenied, view.dispatch, request, report_id=sac.report_id)

    def test_has_role(self):
        user = baker.make(User)
        sac = baker.make(SingleAuditChecklist)

        baker.make(Access, sac=sac, user=user, role="certifying_auditor_contact")

        factory = RequestFactory()
        request = factory.get("/")

        request.user = user

        view = self.ViewStub()
        view.dispatch(request, report_id=sac.report_id)
