from ...historic_data_loader import load_historic_data_for_year

from django.core.management.base import BaseCommand

import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Command(BaseCommand):
    help = """
        Migrate from Census tables to GSAFAC tables for a given year. Optionally, you can
        provide a range of dbkeys that will be iterated over to limit the migration.
        Usage:
        manage.py run_migration --year <audit_year> --start <start dbkey> --end <end dbkey>
    """

    def add_arguments(self, parser):
        parser.add_argument("--year", help="4-digit Audit Year")
        parser.add_argument("--start", help="Start dbkey", type=int, default=0)
        parser.add_argument("--end", help="End dbkey", type=int, default=9999)

    def handle(self, *args, **options):
        year = options.get("year")
        if not year:
            print("Please specify an audit year")
            return

        start_dbkey = options.get("start")
        end_dbkey = options.get("end")

        load_historic_data_for_year(year, start_dbkey, end_dbkey)
