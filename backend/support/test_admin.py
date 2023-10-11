from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from users.models import StaffUser, StaffUserLog

User = get_user_model()


class StaffUserAdminTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.superuser = User.objects.create_superuser(
            username="roor",
            password="testpassword",
            email="root@test.com",
        )
        self.user = User(
            username="testuser", password="testpassword", email="testemail@test.com"
        )
        self.url_prefix = "admin:users_staffuser"

    def test_make_user_staff_then_create_user(self):
        # first test that a super user can add a staff user
        self.client.force_login(self.superuser)
        self.client.post(
            reverse(f"{self.url_prefix}_add"),
            data={"staff_email": self.user.email},
        )
        staff = StaffUser.objects.filter(staff_email=self.user.email)
        self.assertEqual(len(staff), 1)
        self.assertEqual(staff.first().added_by_email, self.superuser.email)

        # test that when the user is now created, they have is_staff set to True
        User.objects.create_user(
            username=self.user.username,
            password=self.user.password,
            email=self.user.email,
        )
        added_users = User.objects.filter(email=self.user.email)
        self.assertEqual(len(added_users), 1)
        added_user = added_users.first()
        self.assertTrue(added_user.is_staff)

        # test that a staff user can view the list
        self.client.force_login(added_user)
        response = self.client.get(reverse(f"{self.url_prefix}_changelist"))
        self.assertContains(response, added_user.email)

        # test that a staff user cannot add to the lisy
        response = self.client.post(
            reverse(f"{self.url_prefix}_add"),
            data={"staff_email": "another@test.gov"},
        )
        self.assertGreaterEqual(response.status_code, 400)

    def test_create_user_then_make_user_staff(self):
        User.objects.create_user(
            username=self.user.username,
            password=self.user.password,
            email=self.user.email,
        )
        self.client.force_login(self.superuser)
        self.client.post(
            reverse(f"{self.url_prefix}_add"),
            data={"staff_email": self.user.email},
        )
        added_users = User.objects.filter(email=self.user.email)
        self.assertEqual(len(added_users), 1)
        added_user = added_users.first()
        self.assertTrue(added_user.is_staff)

    def test_make_user_nonstaff(self):
        User.objects.create_user(
            username=self.user.username,
            password=self.user.password,
            email=self.user.email,
        )
        self.client.force_login(self.superuser)
        self.client.post(
            reverse(f"{self.url_prefix}_add"),
            data={"staff_email": self.user.email},
        )
        staff = StaffUser.objects.get(staff_email=self.user.email)

        response = self.client.post(
            reverse(f"{self.url_prefix}_delete", kwargs={"object_id": staff.pk})
            # reverse(f"{self.url_prefix}_changelist"),
            # data={"action": "delete_selected", "_selected_action": [staff.pk]},
        )
        csrf_token = response.context["csrf_token"]
        post_data = {
            "csrfmiddlewaretoken": str(csrf_token),
            "post": "yes",  # This indicates confirmation of deletion
        }
        self.client.post(
            reverse(f"{self.url_prefix}_delete", kwargs={"object_id": staff.pk}),
            data=post_data,
        )
        staff = StaffUser.objects.filter(staff_email=self.user.email)
        self.assertEqual(len(staff), 0)
        staff_logs = StaffUserLog.objects.filter(staff_email=self.user.email)
        self.assertEqual(len(staff_logs), 1)
