from census_historical_migration.sac_general_lib.utils import normalize_year_string
from ...historic_data_loader import load_historic_data_for_year

from django.core.management.base import BaseCommand

import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


class Command(BaseCommand):
    help = """
        Migrate from Census tables to GSAFAC tables for a given year
        Usage:
        manage.py run_migration_for_year --year <audit_year>
    """

    def add_arguments(self, parser):
        parser.add_argument("--year", help="4-digit Audit Year")

    def handle(self, *args, **options):
        year = normalize_year_string(options.get("year"))

        load_historic_data_for_year(audit_year=year)
