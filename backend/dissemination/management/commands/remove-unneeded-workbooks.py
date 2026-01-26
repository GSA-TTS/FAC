from django.core.management.base import BaseCommand
from dissemination.remove_workbook_artifacts import delete_workbooks

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Delete workbook artifacts for a specific partition of disseminated reports."

    def add_arguments(self, parser):
        parser.add_argument(
            "--partition_number",
            type=int,
            required=True,
            help="The partition number to process (e.g., 1, 2, 3).",
        )
        parser.add_argument(
            "--total_partitions",
            type=int,
            required=True,
            help="The total number of partitions (e.g., 4 if splitting the load into four parts).",
        )
        parser.add_argument(
            "--page_size",
            type=int,
            required=False,
            default=10,
            help="Number of items to process per page",
        )
        parser.add_argument(
            "--pages",
            type=int,
            required=False,
            default=None,
            help="Maximum number of pages to process",
        )

    def handle(self, *args, **options):
        partition_number = options["partition_number"]
        total_partitions = options["total_partitions"]
        page_size = options["page_size"]
        pages = options["pages"]

        self.stdout.write(
            self.style.SUCCESS(
                f"Processing partition {partition_number} of {total_partitions}"
            )
        )
        delete_workbooks(
            partition_number, total_partitions, page_size=page_size, pages=pages
        )
