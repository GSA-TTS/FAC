import json
import tempfile

from openpyxl import load_workbook
from audit.intakelib.intermediate_representation import extract_workbook_as_ir
from census_historical_migration.workbooklib.excel_creation_utils import (
    get_audit_header,
)
from census_historical_migration.sac_general_lib.utils import (
    normalize_year_string_or_exit,
)
from census_historical_migration.workbooklib.workbook_builder import (
    generate_workbook,
)
from census_historical_migration.workbooklib.workbook_section_handlers import (
    sections_to_handlers,
)
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
        parser.add_argument("--output", type=str, required=True)
        parser.add_argument("--dbkey", type=str, required=True)
        parser.add_argument("--year", type=str, default="22")
        parser.add_argument("--output_type", type=str, default="xlsx")

    def handle(self, *args, **options):  # noqa: C901
        out_basedir = None
        if options["output"]:
            out_basedir = options["output"]
        else:
            out_basedir = "output"

        if not os.path.exists(out_basedir):
            try:
                os.mkdir(out_basedir)
                logger.info(f"Made directory {out_basedir}")
            except Exception as e:
                logger.info(e)
                logger.info(f"Could not create directory {out_basedir}")
                sys.exit()
        year = normalize_year_string_or_exit(options["year"])
        out_dir = os.path.join(out_basedir, f'{options["dbkey"]}-{year[-2:]}')

        if not os.path.exists(out_dir):
            try:
                os.mkdir(out_dir)
                logger.info(f"Made directory {out_dir}")
            except Exception as e:
                logger.info(e)
                logger.info("could not create output directory. exiting.")
                sys.exit()

        audit_header = get_audit_header(options["dbkey"], year)
        output_type = options["output_type"]
        for section, fun in sections_to_handlers.items():
            (wb, _, filename) = generate_workbook(fun, audit_header, section)

            if wb and output_type == "json":
                filename = filename.split(".")[0]
                wb_path = os.path.join(out_dir, f"{filename}.json")

                # Save the workbook to a temporary file to ensure formulas are evaluated
                with tempfile.NamedTemporaryFile(
                    suffix=".xlsx", delete=False
                ) as tmp_file:
                    tmp_path = tmp_file.name
                    wb.save(tmp_path)
                try:
                    # Re-load the workbook to ensure formulas are evaluated
                    wb = load_workbook(tmp_path, data_only=True)
                    with open(wb_path, "w") as f:
                        ir = extract_workbook_as_ir(wb)
                        f.write(json.dumps(ir, indent=4))
                finally:
                    os.remove(tmp_path)

            elif wb:
                wb_path = os.path.join(out_dir, filename)
                wb.save(wb_path)
