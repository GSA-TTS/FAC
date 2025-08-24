from pathlib import Path
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from model_bakery import baker
from audit.test_viewlib.test_compare_submissions import setup_mock_db
from audit.models import Access, SingleAuditChecklist
from users.models import UserPermission, Permission
from django.db.utils import IntegrityError

User = get_user_model()


class Params:
    pass


def setup_test(is_federal=False):
    # Clean up the test db
    # I've found that it caches things in some contexts, so
    # this is a rude/forceful way to make sure the only objects are the ones
    # created during this run. Also makes sure that `.get()` operations do not fail
    # on repeated testing runs.
    for p in Permission.objects.all():
        p.delete()
    for a in Access.objects.all():
        a.delete()
    for up in UserPermission.objects.all():
        up.delete()
    for sac in SingleAuditChecklist.objects.all():
        sac.delete()

    if is_federal:
        try:
            rtp = Permission.objects.get(slug=Permission.PermissionType.READ_TRIBAL)
        except IntegrityError:
            # This exception is wrong. I'm trying to work around the test DB holding on to things.
            rtp = baker.make(Permission, slug=Permission.PermissionType.READ_TRIBAL)

    # I need to be a valid user...
    p = Params()
    p.user = baker.make(User)

    if is_federal:
        baker.make(
            UserPermission,
            user=p.user,
            permission=rtp,
        )
    else:
        baker.make(
            UserPermission,
            user=p.user,
        )

    p.sacs = setup_mock_db()

    for sac in p.sacs:
        print(f"Creating access for user {p.user.id} report {sac.report_id}")
        baker.make(Access, user=p.user, sac=sac)

    p.client = Client()
    return p


class CompareSubmissionsViewTests(TestCase):
    view = "audit:CompareSubmissions"

    def test_login_required(self):
        """Check that login is required"""
        p = setup_test()
        p.client.force_login(user=p.user)
        response = p.client.get(
            reverse(
                self.view,
                kwargs={"report_id": "2025-01-FAKEDB-0000000002"},
            ),
            follow=True,
        )
        self.assertTemplateUsed(response, "audit/compare_submissions.html")

    def test_phrase_in_page(self):
        """Check for report ID in form."""
        p = setup_test()
        p.client.force_login(user=p.user)
        res = p.client.get(
            reverse(
                self.view,
                kwargs={"report_id": "2025-01-FAKEDB-0000000002"},
            ),
            follow=True,
        )
        # I get an auth error.
        self.assertIn("2025-01-FAKEDB-0000000002", res.content.decode("utf-8"))
