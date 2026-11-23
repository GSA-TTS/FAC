from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse, NoReverseMatch
from model_bakery import baker
from audit.test_viewlib.test_compare_submissions import setup_mock_db

from audit.models import Access, SingleAuditChecklist
from users.models import UserPermission, Permission
from audit.views.compare_submissions_view import (
    _has_sensitive_data,
    _compare_sac,
    _get_comparison_permissions,
    _get_search_show_all_data,
    _get_submissions_show_all_data,
    _get_previous_report_id,
)

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
        # create a random fed user w/out access to audits
        p.feduser = baker.make(User)

    if is_federal:
        print("Granting federal access")
        baker.make(
            UserPermission,
            user=p.user,
            permission=rtp,
        )

        baker.make(
            UserPermission,
            user=p.feduser,
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

    def test_phrase_in_page_success(self):
        """Check for report ID in form."""
        p = setup_test()
        p.client.force_login(user=p.user)

        # Three tests
        # If we look for #2, we will default to comparing with its prev, which is 1
        # If we look for #3, we default to its prev, which is 2
        # If we look for #4, we default to its prev, which is 4
        for pair in [[1, 2], [2, 3], [4, 5]]:
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

    def test_phrase_in_page_fail(self):
        """Check for report ID in form."""
        p = setup_test()
        p.client.force_login(user=p.user)

        # two tests
        # If we look for #1, we have no prev, we drop out
        # while the underlying code in 'compare_report_ids' defaults 
        # to using 'next' if 'previous' is missing.  In our view we don't allow this
        #
        for pair in [[2, 1], [5,4]]:
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
            self.assertNotIn(f"000000000{pair[0]}", content)
            self.assertNotIn(f"000000000{pair[1]}", content)


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

    def test_fail_no_previous_with_submission(self):
        p = setup_test()
        p.client.force_login(user=p.user)

        response = p.client.get(
            reverse(
                self.view,
                kwargs={"report_id": "2025-01-FAKEDB-0000000001", "route": "submission"},
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 403)

    def test_old_fed_with_access_on_submission(self):
        """A fed user with fed privledges ripped away but is an auditee/auditor on the audit"""
        p = setup_test(is_federal=True)

        # we rip fed access away from this user
        # The only way I can have access is if it recognizes my Federal status
        for up in UserPermission.objects.all():
            up.delete()
        for up in Permission.objects.all():
            up.delete()

        p.client.force_login(user=p.user)

        response = p.client.get(
            reverse(
                self.view,
                kwargs={"report_id": "2025-01-FAKEDB-0000000002", "route": "submission"},
            ),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

    def test_feds_with_no_access_on_submission(self):
        p = setup_test(is_federal=True)

        p.client.force_login(user=p.feduser)

        # All tests should fail,
        # - i am a Federal user that is not on any audits!!
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

    def test_search_summary_for_in_progress_report(self):
        """user w/ access can view an comparison w/ an audit that is in-progress"""
        p = setup_test(is_federal=True)

        # we rip fed access away from this user
        # The only way I can have access is if it recognizes my Federal status
        for up in UserPermission.objects.all():
            up.delete()
        for up in Permission.objects.all():
            up.delete()

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

    def test_findings_text_is_missing(self):
        """unauthenticated user can not view tribal private data"""
        p = setup_test()

        response = p.client.get(
            reverse(
                self.view,
                kwargs={"report_id": "2025-01-FAKEDB-0000000005", "route": "search"},
            ),
            follow=True,
        )

        content = response.content.decode("utf-8")
        self.assertNotIn("Findings Text", content)

    def test_tribal_consent(self):
        sacs = setup_mock_db()
        sac_r5 = sacs[4]

        has_private_tribal = _has_sensitive_data(sac_r5)

        self.assertTrue(has_private_tribal)

    def test_tribal_none_consent(self):
        sacs = setup_mock_db()
        sac_r3 = sacs[2]

        has_private_tribal = _has_sensitive_data(sac_r3)

        self.assertFalse(has_private_tribal)

    def test_compare_sac(self):
        sacs = setup_mock_db()
        sac_r5 = sacs[4]

        context = _compare_sac(sac_r5, True)
        self.assertTrue(context["has_diffs"])
        self.assertFalse(context["has_error"])
        self.assertEqual(context["r1"], "2025-01-FAKEDB-0000000004")
        self.assertEqual(context["r2"], "2025-01-FAKEDB-0000000005")

    def test_comparison_permissions(self):
        p = setup_test()

        sac_r4 = p.sacs[3]
        sac_r5 = p.sacs[4]

        permissions = _get_comparison_permissions(p.user, sac_r4, sac_r5)
        self.assertTrue(permissions["is_auth_user"])
        self.assertTrue(permissions["has_private_tribal"])
        self.assertTrue(permissions["is_on_audit"])

    def test_get_search_show_all_data(self):
        p = setup_test()

        sac_r4 = p.sacs[3]
        sac_r5 = p.sacs[4]

        permissions = _get_comparison_permissions(p.user, sac_r4, sac_r5)
        show_all_data = _get_search_show_all_data(sac_r5, permissions)

        self.assertTrue(show_all_data)

    def test_get_submission_show_all_data(self):
        p = setup_test()

        sac_r4 = p.sacs[3]
        sac_r5 = p.sacs[4]

        permissions = _get_comparison_permissions(p.user, sac_r4, sac_r5)
        show_all_data = _get_submissions_show_all_data(permissions)

        self.assertTrue(show_all_data)

    def test_get_previous_report_id(self):
        p = setup_test()

        sac_r5 = p.sacs[4]

        previous_report_id = _get_previous_report_id(sac_r5)
        self.assertEqual(previous_report_id, "2025-01-FAKEDB-0000000004")

    def test_fail_incorrect_path(self):
        """Check that our url path must be have 'search' or 'submission' in it"""

        # this returns a 404
        with self.assertRaises(NoReverseMatch):
            reverse(
                self.view,
                kwargs={"report_id": "2025-01-FAKEDB-0000000001", "route": "booya"},
            )
