from django.test import TestCase
from model_bakery import baker
from .models import DeletedAccess


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
        at = deleted.removed_at
        by = deleted.removed_by_email
        expected = f"{email} as {role} deleted by {by} at {at}"
        self.assertEqual(str(deleted), expected)
