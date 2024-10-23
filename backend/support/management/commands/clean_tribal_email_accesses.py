from django.core.management.base import BaseCommand
from django.db.models import Count
from django.db.models.functions import Lower
import logging
from users.models import UserPermission

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command for cleaning up tribal access emails.
    This includes lowercasing all emails, and also deleting duplicates (with null user field).
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            action="store_true",
            help="Only logs the number of duplicates without modifying the database.",
        )

    def handle(self, *args, **options):

        fixed_emails = 0
        removed_duplicates = 0

        # first, gather number of duplicate emails that exist.
        duplicates = (
            UserPermission.objects.values(loweremail=Lower("email"))
            .annotate(ecount=Count("id"))
            .filter(ecount__gt=1)
        )
        logger.info(
            f"Identified {duplicates.count()} duplicate emails for tribal access."
        )

        if options.get("count"):
            exit(0)

        # then, lowercase all emails.
        userpermissions = UserPermission.objects.all()
        for userpermission in userpermissions:
            if userpermission.email:
                if userpermission.email != userpermission.email.lower():
                    userpermission.email = userpermission.email.lower()
                    userpermission.save()
                    fixed_emails += 1
        logger.info(f"Removed uppercasing on {fixed_emails} tribal access emails.")

        # finally, remove duplicates (that have a null user field).
        userpermissions = UserPermission.objects.filter(user=None)
        for userpermission in userpermissions:
            if (
                UserPermission.objects.filter(email=userpermission.email)
                .exclude(user=None)
                .exists()
            ):
                userpermission.delete()
                removed_duplicates += 1
        logger.info(
            f"Removed 'blank user' for {removed_duplicates} duplicate tribal access emails."
        )
