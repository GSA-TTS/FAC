from ...historic_data_loader import load_historic_data_for_year

from django.core.management.base import BaseCommand

import logging
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Command(BaseCommand):
    help = """
        Migrate from Census tables to GSAFAC tables for a given year. Optionally, you can
        provide a range of dbkeys that will be iterated over to limit the migration.
        Usage:
        manage.py run_migration --year <audit_year> --dbkeys <comma separated dbkeys>
    """

    def add_arguments(self, parser):
        parser.add_argument("--year", help="4-digit Audit Year")
        parser.add_argument("--dbkeys", type=str, required=False, default="0, 9999")

    def handle(self, *args, **options):
        year = options.get("year")
        if not year:
            print("Please specify an audit year")
            return

        try:
            dbkeys_str = options["dbkeys"]
            dbkeys = list(map(lambda d: int(d), dbkeys_str.split(",")))
            start_dbkey = min(dbkeys)
            end_dbkey = max(dbkeys)
        except ValueError:
            logger.error(f"Found a non-integer in dbkeys '{dbkeys_str}'")
            sys.exit(-1)

        load_historic_data_for_year(year, start_dbkey, end_dbkey)
