from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.db import transaction
from users.models import StaffUser
import json
import logging
import os

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        """Create a group with readonly permissions."""
        group_readonly, created = Group.objects.get_or_create(name="Read-only")
        readonly_codenames = [
            "view_access",
            "view_deletedaccess",
            "view_singleauditchecklist",
            "view_sacvalidationwaiver",
            "view_ueivalidationwaiver",
            "view_additionalein",
            "view_additionaluei",
            "view_captext",
            "view_federalaward",
            "view_findingtext",
            "view_finding",
            "view_general",
            "view_note",
            "view_passthrough",
            "view_secondaryauditor",
            "view_cognizantassignment",
            "view_staffuser",
            "view_userpermission",
            "view_tribalapiaccesskeyids",
        ]
        group_readonly.permissions.clear()
        for code in readonly_codenames:
            group_readonly.permissions.add(Permission.objects.get(codename=code))
        group_readonly.save()

        """Create a group with helpdesk permissions."""
        group_helpdesk, created = Group.objects.get_or_create(name="Helpdesk")
        helpdesk_codenames = readonly_codenames + [
            "add_userpermission",
            "change_userpermission",
            "delete_userpermission",
            "add_tribalapiaccesskeyids",
            "change_tribalapiaccesskeyids",
            "delete_tribalapiaccesskeyids",
            "add_sacvalidationwaiver",
            "add_ueivalidationwaiver",
            "add_cognizantassignment",
        ]
        group_helpdesk.permissions.clear()
        for code in helpdesk_codenames:
            group_helpdesk.permissions.add(Permission.objects.get(codename=code))
        group_helpdesk.save()

        # read in staffusers JSON.
        user_list = None
        with open(
            os.path.join(settings.BASE_DIR, "config/staffusers.json"), "r"
        ) as file:
            user_list = json.load(file)

        if user_list:

            # clear superuser privileges.
            superusers = User.objects.filter(is_superuser=True)
            for superuser in superusers:
                superuser.is_superuser = False
                superuser.save()

            # clear existing staff users.
            StaffUser.objects.all().delete()

            for role in user_list:
                for email in user_list[role]:

                    # create staff user for each role.
                    with transaction.atomic():

                        StaffUser(
                            staff_email=email,
                        ).save()

                        # attempt to update the user.
                        user = User.objects.filter(email=email, is_staff=True)

                        if user.exists():
                            user = user.first()
                            user.groups.clear()
                            match role:
                                case "readonly":
                                    user.groups.add(group_readonly)
                                case "helpdesk":
                                    user.groups.clear()
                                    user.groups.add(group_helpdesk)
                                case "superuser":
                                    user.is_superuser = True

                            user.save()
                            logger.info(f"Synced {email} to a StaffUser role.")

                        else:
                            transaction.set_rollback(True)
                            logger.warning(
                                f"StaffUser not created for {email}, they have not logged in yet."
                            )
