"""load_fixtures command.

Load fixture data into the database.
"""

import logging

from django.core.management.base import BaseCommand

from audit.fixtures.single_audit_checklist import load_single_audit_checklists

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        load_single_audit_checklists()
        logger.info("All fixtures loaded.")
