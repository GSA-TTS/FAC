import json

from openpyxl import load_workbook
from audit.intakelib.intermediate_representation import extract_workbook_as_ir
from django.core.management.base import BaseCommand

import os
import sys
import argparse
import pprint
import logging


pp = pprint.PrettyPrinter(indent=2)

parser = argparse.ArgumentParser()

logger = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            required=True,
            help="The directory containing XLSX files to convert",
        )

    def handle(self, *args, **options):  # noqa: C901
        output_path = options["output"]

        if not os.path.exists(output_path):
            logger.info(f'The directory "{output_path}" does not exist.')
            sys.exit()

        xlsx_files = [f for f in os.listdir(output_path) if f.endswith(".xlsx")]

        if not xlsx_files:
            logger.info(f"No XLSX files found in {output_path}")
            sys.exit()

        for xlsx_file in xlsx_files:
            xlsx_file_path = os.path.join(output_path, xlsx_file)
            json_file_path = os.path.join(
                output_path, f"{os.path.splitext(xlsx_file)[0]}.json"
            )

            try:
                # Load the workbook to ensure formulas are evaluated
                wb = load_workbook(xlsx_file_path, data_only=True)

                # Extract the workbook as IR (Intermediate Representation)
                ir = extract_workbook_as_ir(wb)

                with open(json_file_path, "w") as json_file:
                    json.dump(ir, json_file, indent=4)

                logger.info(f"Converted {xlsx_file} to {json_file_path}")

            except Exception as e:
                logger.error(f"Failed to convert {xlsx_file}: {str(e)}")
                sys.exit(-1)
