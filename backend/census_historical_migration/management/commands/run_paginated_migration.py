from census_historical_migration.sac_general_lib.utils import (
    normalize_year_string_or_exit,
)
from ...historic_data_loader import load_historic_data_for_year

from django.core.management.base import BaseCommand

import logging
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Command(BaseCommand):
    help = """
        Migrate from Census tables to GSAFAC tables for a given year using pagination
        Usage:
        manage.py run_migration
            --year <audit year>
            --page_size <page size>
            --pages <comma separated pages>
    """

    def add_arguments(self, parser):
        parser.add_argument("--year", help="4-digit Audit Year")
        parser.add_argument("--page_size", type=int, required=False, default=5)
        parser.add_argument("--pages", type=str, required=False, default="1")

    def handle(self, *args, **options):
        year = normalize_year_string_or_exit(options.get("year"))

        try:
            pages_str = options["pages"]
            pages = list(map(lambda d: int(d), pages_str.split(",")))
        except ValueError:
            logger.error(f"Found a non-integer in pages '{pages_str}'")
            sys.exit(-1)

        load_historic_data_for_year(year, options["page_size"], pages)
