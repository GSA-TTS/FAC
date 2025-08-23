from django.core.management.base import BaseCommand

import logging
from django.contrib.auth import get_user_model
from pprint import pprint

from audit.compare_two_submissions import compare_with_prev

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

User = get_user_model()


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("report_id", type=str)

    def handle(self, *args, **options):
        rid = options["report_id"]

        # This is actually sneaky. Given a report ID, it either
        # compares to the previous (if one exists), or if no prev
        # exists, but a *next* DOES exist, it flips the order and
        # compares next to this one.
        pprint(compare_with_prev(rid))
