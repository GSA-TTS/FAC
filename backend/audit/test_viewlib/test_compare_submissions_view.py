from pathlib import Path
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from model_bakery import baker
from audit.test_viewlib.test_compare_submissions import setup_mock_db
from audit.models import (
    Access,
)
from users.models import UserPermission, Permission
from django.db.utils import IntegrityError
from psycopg2.errors import UniqueViolation

User = get_user_model()

try:
    rtp = baker.make(Permission, slug=Permission.PermissionType.READ_TRIBAL)
except IntegrityError:
    rtp = Permission.objects.get(slug=Permission.PermissionType.READ_TRIBAL)


class CompareSubmissionsViewTests(TestCase):

    is_setup = False

    def setUp(self):
        # I need to be a valid user...
        self.user = baker.make(User)
        baker.make(
            UserPermission,
            user=self.user,
            permission=rtp,
        )
        self.sacs = setup_mock_db()
        for sac in self.sacs:
            baker.make(Access, user=self.user, sac=sac, role="editor")
        self.client = Client()

    def test_login_required(self):
        """Check that login is required"""
        response = self.client.get(
            reverse(
                "audit:CompareSubmissions",
                kwargs={"report_id": "2025-01-FAKEDB-0000000002"},
            )
        )
        # Why is a 302 coming back?
        # I expect a 403.
        self.assertEqual(response.status_code, 302)

        # self.assertTemplateUsed(response, "audit/compare_submissions.html")
        # self.assertTrue(response.context["session_expired"])

    def test_phrase_in_page(self):
        """Check for report ID in form."""
        self.client.force_login(user=self.user)

        phrase = "2025-01-FAKEDB-0000000002"
        res = self.client.get(
            reverse(
                "audit:CompareSubmissions",
                kwargs={"report_id": "2025-01-FAKEDB-0000000002"},
            )
        )
        # I get an auth error.
        self.assertIn(phrase, res.content.decode("utf-8"))
