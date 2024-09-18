from audit.models import (
    Access,
    DeletedAccess,
    delete_access_and_create_record,
)

from django.core.management.base import BaseCommand

import logging
import sys


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command for deleting Access entries with blank email
    fields. A DeletedAccess entry is created for each deleted Access entry by
    using audit.models.delete_access_and_create_record.
    """

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            action="store_true",
            help="Only logs the blank Access entries count without deleting",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Logs info for each Access and DeletedAccess entry being deleted/created",
        )
        parser.add_argument(
            "--limit",
            type=int,
            help="Limits the number of blank Access entries to delete",
            default=None,
        )

    def handle(self, *args, **options):
        access_start_count = len(Access.objects.all())
        logger.info(f"Access count: {access_start_count}")

        deleted_access_start_count = len(DeletedAccess.objects.all())
        logger.info(f"DeletedAccess count: {deleted_access_start_count}")

        blank_accesses = Access.objects.filter(email="")
        logger.info(f"Blank Access count: {len(blank_accesses)}")

        if options.get("count"):
            sys.exit(0)

        limit = options.get("limit")
        if limit is not None:
            logger.info(f"Deletion limit: {limit}")

        deleted_count = 0

        for blank_access in blank_accesses:
            if deleted_count == limit:
                logger.info("Deletion limit reached")
                break

            if options.get("verbose"):
                logger.info(
                    f"Deleting blank Access for {blank_access.sac.report_id}, {blank_access.fullname}"
                )

            _, deletion_record = delete_access_and_create_record(blank_access)

            if options.get("verbose"):
                logger.info(f"Created DeletedAccess {deletion_record.id}")

            deleted_count += 1

        logger.info(f"Deleted {deleted_count} blank Access entries")

        access_finish_count = len(Access.objects.all())
        logger.info(f"Final Access count: {access_finish_count}")

        deleted_access_finish_count = len(DeletedAccess.objects.all())
        logger.info(f"Final DeletedAccess count: {deleted_access_finish_count}")
