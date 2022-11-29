from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from io import StringIO

from model_bakery import baker

User = get_user_model()


class MakeSuperTest(TestCase):
    def test_command_disabled(self):
        """
        The command should raise an error if user promotion commands are disabled in settings
        """
        with self.settings(USER_PROMOTION_COMMANDS_ENABLED=False):
            self.assertRaisesMessage(
                CommandError,
                "This command is currently disabled.",
                call_command,
                "make_super",
                "test@example.com",
            )

    def test_user_does_not_exist(self):
        """
        The command should raise an error when there is no user with the given email address
        """
        out = StringIO()
        email = "notarealemail@example.com"

        self.assertRaises(CommandError, call_command, "make_super", email, stdout=out)

    def test_single_user_updated(self):
        """
        The command should set is_superuser to True and print a message when a single User is found with the given email address
        """
        out = StringIO()
        email = "single@example.com"

        user = baker.make(User, email=email, is_superuser=False)

        call_command("make_super", email, stdout=out)

        updated_user = User.objects.get(pk=user.pk)

        self.assertTrue(updated_user.is_superuser)
        self.assertIn(
            f"User with ID {user.pk} is_superuser set to True", out.getvalue()
        )

    def test_multiple_users_updated(self):
        """
        The command should set is_superuser to True and print a message when multiple Users are found with the given email address
        """
        out = StringIO()
        email = "multiple@example.com"

        user1 = baker.make(User, email=email, is_superuser=False)
        user2 = baker.make(User, email=email, is_superuser=False)

        call_command("make_super", email, stdout=out)

        updated_user1 = User.objects.get(pk=user1.pk)
        updated_user2 = User.objects.get(pk=user2.pk)

        self.assertTrue(updated_user1.is_superuser)
        self.assertTrue(updated_user2.is_superuser)
        self.assertIn(
            f"User with ID {user1.pk} is_superuser set to True", out.getvalue()
        )
        self.assertIn(
            f"User with ID {user2.pk} is_superuser set to True", out.getvalue()
        )
