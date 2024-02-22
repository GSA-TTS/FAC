import logging
import os
import sys
import openpyxl
import datetime

from django.core.management.base import BaseCommand


logger = logging.getLogger(__name__)


def generate_files(base_xlsx, num_files, output):
    logger.info(f"Loading base XLSX {base_xlsx}...")

    wb = openpyxl.load_workbook(base_xlsx)
    ws = wb.active

    logger.info(f"Creating {num_files} files from {base_xlsx} in {output}")

    for i in range(num_files):
        dt = datetime.datetime.now()
        ws['A1'] = dt
        path = os.path.join(output, f"{dt}.xlsx")
        wb.save(path)
        logger.info(f"#{i + 1} Created: {path}")

    logger.info("Done")


class Command(BaseCommand):
    help = """
        Generates unique XLSX files by slightly modifying copies of the given a base file. Used in conjuction with the
        collect_scan_metrics cmd.
        Usage:
        manage.py generate_xlsx_files --base_xlsx <xlsx file path> --num_files <int>
        Example:
        manage.py generate_xlsx_files --base_xlsx 'output/181744-22/federal-awards-workbook-181744.xlsx' --num_files 5
    """

    def add_arguments(self, parser):
        parser.add_argument("--output", type=str, required=False, default="./metrics_files")
        parser.add_argument("--base_xlsx", type=str, required=True, default=None)
        parser.add_argument("--num_files", type=int, required=False, default=1)
        pass

    def handle(self, *args, **options):
        output = options["output"]
        base_xlsx = options["base_xlsx"]
        num_files = options["num_files"]

        if not os.path.exists(output):
            try:
                os.mkdir(output)
                logger.info(f"Made directory {output}")
            except Exception as e:
                logger.error(f"Could not create directory {output}: {e}")
                sys.exit()

        if not os.path.exists(base_xlsx):
            logger.error(f"Given base_xlsx {base_xlsx} does not exist")
            sys.exit()

        generate_files(base_xlsx, num_files, output)
