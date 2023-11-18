import logging
import sys

from django.conf import settings
from django.core.management.base import BaseCommand
from ...make_submission import load_historic_data

logger = logging.getLogger(__name__)
ENVIRONMENT = settings.ENVIRONMENT


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--dbkeys", type=str, required=False, default="")
        parser.add_argument("--years", type=str, required=False, default="")

    def handle(self, *args, **options):
        dbkeys_str = options["dbkeys"]
        years_str = options["years"]
        dbkeys = dbkeys_str.split(",")
        years = years_str.split(",")

        if len(dbkeys) != len(years):
            logger.error(
                "Received {} dbkeys and {} years. Must be equal. Exiting.".format(
                    len(dbkeys), len(years)
                )
            )
            sys.exit(-1)

        lengths = [len(s) == 2 for s in years]
        if dbkeys_str and years_str and (not all(lengths)):
            logger.error("Years must be two digits. Exiting.")
            sys.exit(-2)

        defaults = [
            ("183126", "22"),
            # ("181744", "22"),
            # ("191734", "22"),
        ]

        if ENVIRONMENT in ["LOCAL", "DEVELOPMENT", "PREVIEW", "STAGING"]:
            if dbkeys_str and years_str:
                logger.info(
                    f"Generating test reports for DBKEYS: {dbkeys_str} and YEARS: {years_str}"
                )
                for dbkey, year in zip(dbkeys, years):
                    result = load_historic_data("20" + year, dbkey)
                    print(result)
            else:
                for dbkey, year in defaults:
                    logger.info("Running {}-{} end-to-end".format(dbkey, "20" + year))
                    result = load_historic_data("20" + year, dbkey)
                    print(result)
        else:
            logger.error(
                "Cannot run end-to-end workbook generation in production. Exiting."
            )
            sys.exit(-3)
