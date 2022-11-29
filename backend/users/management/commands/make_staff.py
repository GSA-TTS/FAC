from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Update a User with the given email to be a staff user"

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, help="Email address of target user")

    def handle(self, *args, **kwargs):
        if not settings.USER_PROMOTION_COMMANDS_ENABLED:
            raise CommandError("This command is currently disabled.")

        email = kwargs["email"]

        users = User.objects.filter(email=email)

        if not users:
            raise CommandError(f"User with email {email} does not exist")

        for user in users:
            user.is_staff = True
            user.save()
            self.stdout.write(f"User with ID {user.pk} is_staff set to True")
