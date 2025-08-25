from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from model_bakery import baker
from audit.test_viewlib.test_compare_submissions import setup_mock_db
from audit.models import Access, SingleAuditChecklist
from users.models import UserPermission, Permission

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
        except Permission.DoesNotExist:
            rtp = baker.make(Permission, slug=Permission.PermissionType.READ_TRIBAL)

    # I need to be a valid user...
    p = Params()
    p.user = baker.make(User)

    if is_federal:
        print("Granting federal access")
        baker.make(
            UserPermission,
            user=p.user,
            permission=rtp,
        )

    p.sacs = setup_mock_db()

    for sac in p.sacs:
        # print(f"Creating access for user {p.user.id} report {sac.report_id}")
        baker.make(Access, user=p.user, sac=sac)

    p.client = Client()
    p.audit_range = len(p.sacs) + 1
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

        # Three tests
        # If we look for #2, we will default to comparing with its prev, which is 1
        # If we look for 3, we default to its prev, which is 2
        # If we look for #1, we have no prev, but we have a next, so we compare against #2
        # This helps users get *something* back in most/all cases when in a resubmission chain.
        # EG if you look for the first or last, you get *something* compared as a result.
        for pair in [[1, 2], [2, 3], [2, 1]]:
            res = p.client.get(
                reverse(
                    self.view,
                    kwargs={"report_id": f"2025-01-FAKEDB-000000000{pair[1]}"},
                ),
                follow=True,
            )
            content = res.content.decode("utf-8")
            self.assertIn(f"000000000{pair[0]}", content)
            self.assertIn(f"000000000{pair[1]}", content)

    def test_fail_without_access_to_audit(self):
        """Check I cannot access a report if I don't have an access object"""
        p = setup_test()

        # This should delete the access objects
        # That way, I cannot access anything in this test.
        for a in Access.objects.all():
            a.delete()

        p.client.force_login(user=p.user)

        # All of the  test audits should fail, as we wiped out the access objects.
        for counter in range(1, p.audit_range):
            res = p.client.get(
                reverse(
                    self.view,
                    kwargs={"report_id": f"2025-01-FAKEDB-000000000{counter}"},
                ),
                follow=True,
            )
            self.assertEqual(res.status_code, 403)

    def test_feds_have_access(self):
        """Check I cannot access a report if I don't have an access object"""
        p = setup_test(is_federal=True)

        # This should delete the access objects
        # The only way I can have access is if it recognizes my Federal status
        for a in Access.objects.all():
            a.delete()

        p.client.force_login(user=p.user)

        # All of the audits should pass, becuase I am now a Federal user.
        for counter in range(1, p.audit_range):
            res = p.client.get(
                reverse(
                    self.view,
                    kwargs={"report_id": f"2025-01-FAKEDB-000000000{counter}"},
                ),
                follow=True,
            )
            self.assertEqual(res.status_code, 200)
