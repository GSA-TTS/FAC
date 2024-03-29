from census_historical_migration.sac_general_lib.utils import (
    normalize_year_string_or_exit,
)
from census_historical_migration.workbooklib.excel_creation_utils import (
    get_audit_header,
)
from census_historical_migration.historic_data_loader import (
    create_or_get_user,
    log_results,
)
from census_historical_migration.migration_result import MigrationResult

from django.core.management.base import BaseCommand
from census_historical_migration.end_to_end_core import run_end_to_end
from django.conf import settings

import logging
import sys


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--dbkeys", type=str, required=False, default="177310,251020"
        )
        parser.add_argument("--years", type=str, required=False, default="22,22")

    def initiate_migration(self, dbkeys_str, years_str):
        dbkeys = dbkeys_str.split(",")

        if years_str:
            years = [
                normalize_year_string_or_exit(year) for year in years_str.split(",")
            ]
            if len(dbkeys) != len(years):
                logger.error(
                    "Received {} dbkeys and {} years. Must be equal. Exiting.".format(
                        len(dbkeys), len(years)
                    )
                )
                sys.exit(-1)

        user = create_or_get_user()

        if dbkeys_str and years_str:
            logger.info(
                f"Generating test reports for DBKEYS: {dbkeys_str} and YEARS: {years_str}"
            )
            total_count = error_count = 0
            for dbkey, year in zip(dbkeys, years):
                logger.info("Running {}-{} end-to-end".format(dbkey, year))

                try:
                    audit_header = get_audit_header(dbkey, year)
                except Exception as e:
                    logger.error(e)
                    continue

                run_end_to_end(user, audit_header)
                MigrationResult.append_summary(year, dbkey)
                total_count += 1

            log_results(error_count, total_count)

    def handle(self, *args, **options):
        dbkeys_str = options["dbkeys"]
        years_str = options["years"]

        if settings.ENVIRONMENT in ["LOCAL", "DEVELOPMENT", "PREVIEW", "STAGING"]:
            self.initiate_migration(dbkeys_str, years_str)
        else:
            logger.error(
                "Cannot run end-to-end historic data  migrator in production. Exiting."
            )
            sys.exit(-3)
