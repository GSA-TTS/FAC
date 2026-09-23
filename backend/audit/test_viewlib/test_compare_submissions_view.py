from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse, NoReverseMatch
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
                kwargs={
                    "report_id": "2025-01-FAKEDB-0000000002",
                    "route": "submission",
                },
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
                    kwargs={
                        "report_id": f"2025-01-FAKEDB-000000000{pair[1]}",
                        "route": "submission",
                    },
                ),
                follow=True,
            )
            content = res.content.decode("utf-8")
            self.assertIn(f"000000000{pair[0]}", content)
            self.assertIn(f"000000000{pair[1]}", content)

    def test_fail_without_access_to_audit(self):
        """test that any ole authenticated user cannot access comparision via the submission route"""
        p = setup_test()

        # this authenticated user is not the auditee / auditor for these SACs

        # This should delete the access objects
        # That way, I cannot access anything in this test.
        for a in Access.objects.all():
            a.delete()

        p.client.force_login(user=p.user)

        # All of the test audits should fail, as we wiped out the access objects.
        for counter in range(1, p.audit_range):
            res = p.client.get(
                reverse(
                    self.view,
                    kwargs={
                        "report_id": f"2025-01-FAKEDB-000000000{counter}",
                        "route": "submission",
                    },
                ),
                follow=True,
            )
            self.assertEqual(res.status_code, 403)

    def test_feds_have_access(self):
        """fed user can view comparisons even if they don't have access"""
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
                    kwargs={
                        "report_id": f"2025-01-FAKEDB-000000000{counter}",
                        "route": "submission",
                    },
                ),
                follow=True,
            )
            self.assertEqual(res.status_code, 200)

    def test_without_login_on_search_summary(self):
        """test unauthenticated user is allowed to view comparison via search summary"""
        p = setup_test()

        response = p.client.get(
            reverse(
                self.view,
                kwargs={"report_id": "2025-01-FAKEDB-0000000002", "route": "search"},
            ),
            follow=True,
        )
        self.assertTemplateUsed(response, "audit/compare_submissions.html")

    def test_fail_on_search_summary_for_in_progress_report(self):
        """test unauthenticated user cannot access to an 'in-progress' report via search summary"""
        p = setup_test()

        # unauthenticated users can only see comparisons on
        # resubmissions that are either 'disseminated' or
        # 'resubmitted'
        response = p.client.get(
            reverse(
                self.view,
                kwargs={"report_id": "2025-01-FAKEDB-0000000003", "route": "search"},
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 403)

    def test_feds_on_search_summary_for_in_progress_report(self):
        """fed user can view an comparison w/ an audit that is in-progress"""
        p = setup_test(is_federal=True)

        # This should delete the access objects
        # The only way I can have access is if it recognizes my Federal status
        for a in Access.objects.all():
            a.delete()

        p.client.force_login(user=p.user)

        response = p.client.get(
            reverse(
                self.view,
                kwargs={"report_id": "2025-01-FAKEDB-0000000003", "route": "search"},
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

    def test_access_on_search_summary_for_in_progress_report(self):
        """auditee/auditor can view a comparison w/ an audit that is in-progress"""
        p = setup_test()

        # this tests an authenticated user as an auditee or auditor
        # has access to view their own in_progress comparison

        p.client.force_login(user=p.user)

        response = p.client.get(
            reverse(
                self.view,
                kwargs={"report_id": "2025-01-FAKEDB-0000000003", "route": "search"},
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

    def test_fail_incorrect_path(self):
        """Check that our url path must be have 'search' or 'submission' in it"""

        # this returns a 404
        with self.assertRaises(NoReverseMatch):
            reverse(
                self.view,
                kwargs={"report_id": "2025-01-FAKEDB-0000000001", "route": "booya"},
            )
