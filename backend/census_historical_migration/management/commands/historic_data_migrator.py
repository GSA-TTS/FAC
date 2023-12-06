import logging
import sys
from backend.census_historical_migration.sac_general_lib.utils import (
    normalize_year_string,
)
from census_historical_migration.historic_data_loader import create_or_get_user

from config.settings import ENVIRONMENT
from django.core.management.base import BaseCommand
from census_historical_migration.workbooklib.end_to_end_core import run_end_to_end

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--dbkeys", type=str, required=False, default="")
        parser.add_argument("--years", type=str, required=False, default="")

    def handle(self, *args, **options):
        dbkeys_str = options["dbkeys"]
        years_str = options["years"]
        dbkeys = dbkeys_str.split(",")
        years = [normalize_year_string(year) for year in years_str.split(",")]

        if len(dbkeys) != len(years):
            logger.error(
                "Received {} dbkeys and {} years. Must be equal. Exiting.".format(
                    len(dbkeys), len(years)
                )
            )
            sys.exit(-1)

        user = create_or_get_user()

        defaults = [
            (177310, 22),
            (251020, 22),
        ]

        if ENVIRONMENT in ["LOCAL", "DEVELOPMENT", "PREVIEW", "STAGING"]:
            if dbkeys_str and years_str:
                logger.info(
                    f"Generating test reports for DBKEYS: {dbkeys_str} and YEARS: {years_str}"
                )
                for dbkey, year in zip(dbkeys, years):
                    result = {"success": [], "errors": []}
                    run_end_to_end(user, dbkey, year, result)
                    logger.info(result)
            else:
                for pair in defaults:
                    logger.info("Running {}-{} end-to-end".format(pair[0], pair[1]))
                    result = {"success": [], "errors": []}
                    year = normalize_year_string(pair[1])
                    run_end_to_end(user, str(pair[0]), year, result)
                    logger.info(result)
        else:
            logger.error(
                "Cannot run end-to-end historic data  migrator in production. Exiting."
            )
            sys.exit(-3)
