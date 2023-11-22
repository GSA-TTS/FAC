from django.test import TestCase
from model_bakery import baker
from .models import (
    Access,
    DeletedAccess,
    SingleAuditChecklist,
    User,
    remove_email_from_submission_access,
)


class DeletedAccessTests(TestCase):
    """Model tests"""

    def test_str_is_correct(self):
        """
        String representation of DeletedAccess instance is:

            {email} as {role} deleted by {by} at {at}"
        """
        deleted = baker.make(DeletedAccess)
        email = deleted.email
        role = deleted.get_role_display()
        del_at = deleted.removed_at
        del_by = deleted.removed_by_email
        expected = f"{email} as {role} deleted by {del_by} at {del_at}"
        self.assertEqual(str(deleted), expected)

    def test_deletion_function_removes_access(self):
        """
        Test calling the deletion function directly.
        """
        user = baker.make(User, email="a@a.com")
        user2 = baker.make(User, email="b@b.com")
        sac = baker.make(SingleAuditChecklist)
        baker.make(Access, user=user, email=user.email, sac=sac, role="editor")
        baker.make(Access, user=user2, email=user2.email, sac=sac, role="editor")
        user_accesses = Access.objects.filter(user=user, sac=sac)
        self.assertEqual(sac.id, user_accesses[0].sac.id)
        user2_accesses = Access.objects.filter(user=user2, sac=sac)
        self.assertEqual(sac.id, user2_accesses[0].sac.id)
        deletion_records = DeletedAccess.objects.filter(sac=sac.id)
        self.assertEqual(0, len(deletion_records))
        results = remove_email_from_submission_access(sac.report_id, user.email)
        self.assertEqual(1, len(results))
        deletion_records_post = DeletedAccess.objects.filter(sac=sac.id)
        self.assertEqual(len(deletion_records_post), len(results))
        self.assertEqual(deletion_records_post[0].sac, sac)
        self.assertEqual(deletion_records_post[0].email, user.email)
        post_accesses = Access.objects.filter(user=user, sac=sac)
        self.assertEqual(0, len(post_accesses))

    def test_no_sac_raises_error(self):
        """
        If no such SAC exists, raise an error.
        """
        with self.assertRaises(SingleAuditChecklist.DoesNotExist):
            remove_email_from_submission_access("not-a-real-report-id", "a@a.com")

    def test_no_access_raises_error(self):
        """
        If no such Access exists, raise an error.
        """
        sac = baker.make(SingleAuditChecklist)
        with self.assertRaises(Access.DoesNotExist):
            remove_email_from_submission_access(sac.report_id, "z@z.com")

    def test_access_delete_method_removes_access(self):
        """
        Test calling the deletion function via Access.delete().
        """
        user = baker.make(User, email="a@a.com")
        user2 = baker.make(User, email="b@b.com")
        sac = baker.make(SingleAuditChecklist)
        baker.make(Access, user=user, email=user.email, sac=sac, role="editor")
        baker.make(Access, user=user2, email=user2.email, sac=sac, role="editor")
        user_accesses = Access.objects.filter(user=user, sac=sac)
        self.assertEqual(sac.id, user_accesses[0].sac.id)
        user2_accesses = Access.objects.filter(user=user2, sac=sac)
        self.assertEqual(sac.id, user2_accesses[0].sac.id)
        access = user_accesses[0]
        deletion_records = DeletedAccess.objects.filter(sac=sac.id)
        self.assertEqual(0, len(deletion_records))
        results = access.delete()
        self.assertEqual((1, {"audit.Access": 1}), results)
        deletion_records_post = DeletedAccess.objects.filter(sac=sac.id)
        self.assertEqual(1, len(deletion_records_post))
        self.assertEqual(deletion_records_post[0].sac, sac)
        self.assertEqual(deletion_records_post[0].email, user.email)
        post_accesses = Access.objects.filter(user=user, sac=sac)
        self.assertEqual(0, len(post_accesses))
