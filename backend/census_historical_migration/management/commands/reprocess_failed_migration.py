from census_historical_migration.process_failed_migration import (
    reprocess_failed_reports,
)
from census_historical_migration.sac_general_lib.utils import (
    normalize_year_string_or_exit,
)

from django.core.management.base import BaseCommand

import logging
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Command(BaseCommand):
    help = """
        Reprocess failed migration reports for a given year and error tag using pagination
        Usage:
        manage.py run_migration
            --year <audit year>
            --page_size <page size>
            --pages <comma separated pages>
            --error_tag <error tag>
    """

    def add_arguments(self, parser):
        parser.add_argument("--year", help="Audit Year")
        parser.add_argument("--page_size", help="Number of records by page", type=int)
        parser.add_argument("--pages", help="comma separated pages", type=str)
        parser.add_argument("--error_tag", help="error tag", type=str)

    def handle(self, *args, **options):
        year = normalize_year_string_or_exit(options.get("year"))

        try:
            pages_str = options["pages"]
            pages = list(map(lambda d: int(d), pages_str.split(",")))
        except ValueError:
            logger.error(f"Found a non-integer in pages '{pages_str}'")
            sys.exit(-1)

        reprocess_failed_reports(
            year, options["page_size"], pages, options["error_tag"]
        )
