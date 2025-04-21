from django.contrib.auth.models import User
from django.test import TestCase

from model_bakery import baker
from .models import (
    Access,
    DeletedAccess,
    Audit,
    remove_email_from_submission_access,
)


def _make_test_users_by_email(emails: list[str]) -> list[User]:
    return [baker.make(User, email=email) for email in emails]


def _make_access(audit: Audit, role: str, user: User) -> Access:
    return baker.make(Access, user=user, email=user.email, audit=audit, role=role)


def _make_accesses(audit: Audit, role: str, users: list[User]) -> list[Access]:
    return [_make_access(audit, role, user) for user in users]


class DeletedAccessTests(TestCase):
    """Model tests"""

    def test_str_is_correct(self):
        """
        String representation of DeletedAccess instance is:

            {email} as {role} deleted by {by} at {at}"
        """
        audit = baker.make(Audit, version=0)
        deleted = baker.make(DeletedAccess, audit=audit)
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
        user1, user2 = _make_test_users_by_email(["a@a.com", "b@b.com"])

        audit = baker.make(Audit, version=0)
        _make_accesses(audit, "editor", [user1, user2])
        user1_access = Access.objects.get(user=user1, audit=audit)
        user2_access = Access.objects.get(user=user2, audit=audit)
        deletion_records = DeletedAccess.objects.filter(audit=audit)

        self.assertEqual(audit.id, user1_access.audit.id)
        self.assertEqual(audit.id, user2_access.audit.id)
        self.assertEqual(0, len(deletion_records))

        results = remove_email_from_submission_access(
            audit.report_id, user1.email, role="editor", removing_user=user2
        )
        deletion_record_after = DeletedAccess.objects.get(audit=audit)
        user1_accesses_after = Access.objects.filter(user=user1, audit=audit)
        user2_accesses_after = Access.objects.filter(user=user2, audit=audit)

        self.assertEqual(1, len(results))
        self.assertEqual(deletion_record_after.audit, audit)
        self.assertEqual(deletion_record_after.email, user1.email)
        self.assertEqual(0, len(user1_accesses_after))
        self.assertEqual(1, len(user2_accesses_after))

    def test_deletion_function_removes_only_specific_role(self):
        """
        Test calling the deletion function directly.
        """
        user = _make_test_users_by_email(["a@a.com"])[0]
        audit = baker.make(Audit, version=0)

        _make_access(audit, "editor", user)
        _make_access(audit, "certifying_auditee_contact", user)
        editor_access = Access.objects.get(user=user, audit=audit, role="editor")
        certifying_access = Access.objects.get(
            user=user, audit=audit, role="certifying_auditee_contact"
        )
        deletion_records = DeletedAccess.objects.filter(audit=audit)

        self.assertEqual(audit.id, editor_access.audit.id)
        self.assertEqual(audit.id, certifying_access.audit.id)
        self.assertEqual(0, len(deletion_records))

        results = remove_email_from_submission_access(
            audit.report_id,
            user.email,
            role="certifying_auditee_contact",
            removing_user=user,
        )
        deletion_record_after = DeletedAccess.objects.get(audit=audit)
        editor_accesses_after = Access.objects.filter(
            user=user, audit=audit, role="editor"
        )
        certifying_accesses_after = Access.objects.filter(
            user=user, audit=audit, role="certifying_auditee_contact"
        )

        self.assertEqual(1, len(results))
        self.assertEqual(deletion_record_after.audit, audit)
        self.assertEqual(deletion_record_after.email, user.email)
        self.assertEqual(0, len(certifying_accesses_after))
        self.assertEqual(1, len(editor_accesses_after))

    def test_no_audit_raises_error(self):
        """
        If no such Audit exists, raise an error.
        """
        with self.assertRaises(Audit.DoesNotExist):
            remove_email_from_submission_access(
                "not-a-real-report-id", "a@a.com", "editor"
            )

    def test_no_access_raises_error(self):
        """
        If no such Access exists, raise an error.
        """
        audit = baker.make(Audit, version=0)
        with self.assertRaises(Access.DoesNotExist):
            remove_email_from_submission_access(audit.report_id, "z@z.com", "editor")

    def test_access_delete_method_removes_access(self):
        """
        Test calling the deletion function via Access.delete().
        """
        user1, user2 = _make_test_users_by_email(["a@a.com", "b@b.com"])
        audit = baker.make(Audit, version=0)
        _make_accesses(audit, "editor", [user1, user2])
        user1_access = Access.objects.get(user=user1, audit=audit)
        user2_access = Access.objects.get(user=user2, audit=audit)
        deletion_records = DeletedAccess.objects.filter(audit=audit)

        self.assertEqual(audit.id, user1_access.audit.id)
        self.assertEqual(audit.id, user2_access.audit.id)
        self.assertEqual(0, len(deletion_records))

        removing_user = baker.make(User)
        results = user1_access.delete(removing_user=removing_user)
        deletion_record_after = DeletedAccess.objects.get(audit=audit)
        user1_accesses_after = Access.objects.filter(user=user1, audit=audit)
        user2_accesses_after = Access.objects.filter(user=user2, audit=audit)

        self.assertEqual((1, {"audit.Access": 1}), results)
        self.assertEqual(deletion_record_after.audit, audit)
        self.assertEqual(deletion_record_after.email, user1.email)
        self.assertEqual(0, len(user1_accesses_after))
        self.assertEqual(1, len(user2_accesses_after))

    def test_deletion_function_passes_args(self):
        """
        Test calling the deletion function directly.
        """
        user1, user2 = _make_test_users_by_email(["a@a.com", "b@b.com"])
        audit = baker.make(Audit, version=0)
        _make_accesses(audit, "editor", [user1, user2])
        user1_access = Access.objects.get(user=user1, audit=audit)
        user2_access = Access.objects.get(user=user2, audit=audit)
        deletion_records = DeletedAccess.objects.filter(audit=audit)

        self.assertEqual(audit.id, user1_access.audit.id)
        self.assertEqual(audit.id, user2_access.audit.id)
        self.assertEqual(0, len(deletion_records))

        results = remove_email_from_submission_access(
            audit.report_id,
            user1.email,
            role="editor",
            removing_user=user2,
            event="some-event",
        )
        deletion_record_after = DeletedAccess.objects.get(audit=audit)
        user1_accesses_after = Access.objects.filter(user=user1, audit=audit)

        self.assertEqual(1, len(results))
        self.assertEqual(deletion_record_after.email, user1.email)
        self.assertEqual(0, len(user1_accesses_after))
        self.assertEqual(deletion_record_after.removed_by_user, user2)
        self.assertEqual(deletion_record_after.removal_event, "some-event")
