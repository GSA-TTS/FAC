"""load_fixtures command.

Load fixture data into the database.
"""

import logging

from django.core.management.base import BaseCommand

from audit.fixtures import load_single_audit_checklists
from users.fixtures import load_users

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        # load users first so later fixtures will load items for them
        load_users()
        load_single_audit_checklists()
        logger.info("All fixtures loaded.")
