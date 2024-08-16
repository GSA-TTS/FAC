from django.core.management.base import BaseCommand
from dissemination.remove_workbook_artifacts import delete_workbooks

import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Delete workbook artifacts for specified years"

    def add_arguments(self, parser):
        parser.add_argument(
            "--year",
            type=int,
            required=True,
            help="Comma-separated list of audit years to process",
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
            default=100,
            help="Maximum number of pages to process",
        )

    def handle(self, *args, **options):
        year = options["year"]
        page_size = options["page_size"]
        pages = options["pages"]

        self.stdout.write(self.style.SUCCESS(f"Processing audit year {year}"))
        delete_workbooks(year, page_size=page_size, pages=pages)
