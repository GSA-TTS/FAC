from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.http.response import Http404
from django.test import TestCase
from django.test.client import RequestFactory
from django.views.generic import View

from dissemination.models import General
from dissemination.mixins import ReportAccessRequiredMixin, FederalAccessRequiredMixin

from users.models import Permission, UserPermission

from model_bakery import baker

User = get_user_model()


class ReportAccessRequiredMixinTests(TestCase):
    class ViewStub(ReportAccessRequiredMixin, View):
        def get(self, request, *args, **kwargs):
            pass

    def test_missing_report_id_raises(self):
        request = RequestFactory().get("/")

        self.assertRaises(KeyError, self.ViewStub().dispatch, request)

    def test_nonexistent_report_raises(self):
        request = RequestFactory().get("/")

        self.assertRaises(
            Http404,
            self.ViewStub().dispatch,
            request,
            report_id="not-a-real-report-id",
        )

    def test_public_report_passes(self):
        request = RequestFactory().get("/")

        general = baker.make(General, is_public=True)

        self.ViewStub().dispatch(request, report_id=general.report_id)

    def test_non_public_raises_for_anonymous(self):
        request = RequestFactory().get("/")
        request.user = None

        general = baker.make(General, is_public=False)

        self.assertRaises(
            PermissionDenied,
            self.ViewStub().dispatch,
            request,
            report_id=general.report_id,
        )

    def test_non_public_raises_for_unpermissioned(self):
        request = RequestFactory().get("/")

        user = baker.make(User)
        request.user = user

        general = baker.make(General, is_public=False)

        self.assertRaises(
            PermissionDenied,
            self.ViewStub().dispatch,
            request,
            report_id=general.report_id,
        )

    def test_non_public_passes_for_permissioned(self):
        request = RequestFactory().get("/")

        user = baker.make(User)
        request.user = user

        permission = Permission.objects.get(slug=Permission.PermissionType.READ_TRIBAL)
        baker.make(UserPermission, user=user, email=user.email, permission=permission)

        general = baker.make(General, is_public=False)

        self.ViewStub().dispatch(request, report_id=general.report_id)

    def test_public_passes_for_unpermissioned(self):
        request = RequestFactory().get("/")

        user = baker.make(User)
        request.user = user

        general = baker.make(General, is_public=True)

        self.ViewStub().dispatch(request, report_id=general.report_id)

    def test_public_passes_for_permissioned(self):
        request = RequestFactory().get("/")

        user = baker.make(User)
        request.user = user

        permission = Permission.objects.get(slug=Permission.PermissionType.READ_TRIBAL)
        baker.make(UserPermission, user=user, email=user.email, permission=permission)

        general = baker.make(General, is_public=True)

        self.ViewStub().dispatch(request, report_id=general.report_id)


class FederalAccessRequiredMixinTests(TestCase):
    class ViewStub(FederalAccessRequiredMixin, View):
        def get(self, request, *args, **kwargs):
            pass

    def test_unauthenticated_raises_403(self):
        """
        An unauthenticated user should not be able to access the gated view.
        """
        request = RequestFactory().get("/")

        self.assertRaises(PermissionDenied, self.ViewStub().dispatch, request)

    def test_unprivileged_raises_403(self):
        """
        An authenitcated but unprivileged user should not be able to access the gated view.
        """
        request = RequestFactory().get("/")

        user = baker.make(User)
        request.user = user

        self.assertRaises(PermissionDenied, self.ViewStub().dispatch, request)

    def test_privileged_passes(self):
        """
        An autheniticated and privileged user should be able to access the gated view.
        """
        user = baker.make(User)
        permission = Permission.objects.get(slug=Permission.PermissionType.READ_TRIBAL)
        baker.make(UserPermission, user=user, email=user.email, permission=permission)

        request = RequestFactory().get("/")
        request.user = user

        try:
            self.ViewStub().dispatch(request)
        except PermissionDenied:
            self.fail("Authenticated users should have access.")
