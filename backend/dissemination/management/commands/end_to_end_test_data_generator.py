import os
import logging
import sys
import argparse

from config.settings import ENVIRONMENT
from django.core.management.base import BaseCommand
from dissemination.workbooklib.end_to_end_core import run_end_to_end

CYPRESS_TEST_EMAIL_ADDR = os.getenv("CYPRESS_LOGIN_TEST_EMAIL_AUDITEE")
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--email", type=str, required=False, default=CYPRESS_TEST_EMAIL_ADDR
        )
        parser.add_argument("--dbkeys", type=str, required=False, default="")
        parser.add_argument("--years", type=str, required=False, default="")
        parser.add_argument(
            "--store", action=argparse.BooleanOptionalAction, default=False
        )
        parser.add_argument(
            "--apichecks", action=argparse.BooleanOptionalAction, default=True
        )

    def handle(self, *args, **options):
        dbkeys_str = options["dbkeys"]
        years_str = options["years"]
        email_str = options["email"]
        store_files = options["store"]
        run_api_checks = options["apichecks"]

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
            (182926, 22),
            (181744, 22),
            (191734, 22),
        ]

        if ENVIRONMENT in ["LOCAL", "DEVELOPMENT", "PREVIEW", "STAGING"]:
            if dbkeys_str and years_str:
                logger.info(
                    f"Generating test reports for DBKEYS: {dbkeys_str} and YEARS: {years_str}"
                )
                for dbkey, year in zip(dbkeys, years):
                    run_end_to_end(email_str, dbkey, year, store_files, run_api_checks)
            else:
                for pair in defaults:
                    logger.info("Running {}-{} end-to-end".format(pair[0], pair[1]))
                    run_end_to_end(
                        email_str,
                        str(pair[0]),
                        str(pair[1]),
                        store_files,
                        run_api_checks,
                    )
        else:
            logger.error(
                "Cannot run end-to-end workbook generation in production. Exiting."
            )
            sys.exit(-3)
