"""load_fixtures command.

Load fixture data into the database.
"""

import glob
import logging
import os

from django.core.management.base import BaseCommand

from audit.fixtures.single_audit_checklist import (
    load_single_audit_checklists,
    load_single_audit_checklists_for_email_address,
)

from users.fixtures import load_users

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Django management command for loading fixtures."""

    def add_arguments(self, parser):
        parser.add_argument("email_addresses", nargs="*", type=str)
        parser.add_argument(
            "--workbooks", type=str, help="Directory containing submission workbooks"
        )

    def handle(self, *args, **options):
        # load users first so later fixtures will load items for them
        if not options.get("email_addresses"):
            load_users()
            load_single_audit_checklists()
            logger.info("All fixtures loaded.")
        else:
            # We assume each arg is an email address:
            for email_address in options["email_addresses"]:
                if options["workbooks"] is None:
                    workbooks = []
                else:
                    workbooks = glob.glob(os.path.join(options["workbooks"], "*.xlsx"))
                load_single_audit_checklists_for_email_address(email_address, workbooks)
