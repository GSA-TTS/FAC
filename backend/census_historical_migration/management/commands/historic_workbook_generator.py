from census_historical_migration.workbooklib.excel_creation_utils import (
    set_range,
)
from census_historical_migration.workbooklib.workbook_creation import (
    generate_workbook,
)
from census_historical_migration.workbooklib.workbook_section_handlers import (
    sections_to_handlers,
)
from census_historical_migration.workbooklib.census_models.census import (
    CensusGen22 as Gen,
)

from playhouse.shortcuts import model_to_dict
from django.core.management.base import BaseCommand

import os
import sys
import json
import argparse
import pprint
import logging


pp = pprint.PrettyPrinter(indent=2)

parser = argparse.ArgumentParser()

logger = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)


def set_uei(wb, dbkey):
    g = Gen.select().where(Gen.dbkey == dbkey).get()
    set_range(wb, "auditee_uei", [g.uei])
    return g


def map_simple_columns(wb, mappings, values):
    # Map all the simple ones
    for m in mappings:
        set_range(
            wb,
            m.in_sheet,
            map(lambda v: model_to_dict(v)[m.in_db], values),
            m.default,
            m.type,
        )


# FIXME: Get the padding/shape right on the report_id
def dbkey_to_test_report_id(dbkey):
    g = Gen.select(Gen.audityear, Gen.fyenddate).where(Gen.dbkey == dbkey).get()
    # month = g.fyenddate.split('-')[1]
    # 2022JUN0001000003
    # We start new audits at 1 million.
    # So, we want 10 digits, and zero-pad for
    # historic DBKEY report_ids
    return f"{g.audityear}-TEST-{dbkey.zfill(7)}"


def generate_dissemination_test_table(api_endpoint, dbkey, mappings, objects):
    table = {"rows": list(), "singletons": dict()}
    table["endpoint"] = api_endpoint
    table["report_id"] = dbkey_to_test_report_id(dbkey)
    for o in objects:
        as_dict = model_to_dict(o)
        test_obj = {}
        test_obj["fields"] = []
        test_obj["values"] = []
        for m in mappings:
            # What if we only test non-null values?
            if ((m.in_db in as_dict) and as_dict[m.in_db] is not None) and (
                as_dict[m.in_db] != ""
            ):
                test_obj["fields"].append(m.in_sheet)
                test_obj["values"].append(as_dict[m.in_db])
        table["rows"].append(test_obj)
    return table


def make_file(dir, dbkey, slug):
    return open(os.path.join(dir, f"{slug}-{dbkey}.xlsx"))


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--output", type=str, required=True)
        parser.add_argument("--dbkey", type=str, required=True)
        parser.add_argument("--year", type=str, default="22")

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

        outdir = os.path.join(out_basedir, f'{options["dbkey"]}-{options["year"]}')

        if not os.path.exists(outdir):
            try:
                os.mkdir(outdir)
                logger.info(f"Made directory {outdir}")
            except Exception as e:
                logger.info(e)
                logger.info("could not create output directory. exiting.")
                sys.exit()

        json_test_tables = []
        for section, fun in sections_to_handlers.items():
            (wb, api_json, _, filename) = generate_workbook(
                fun, options["dbkey"], options["year"], section
            )
            if wb:
                wb_path = os.path.join(outdir, filename)
                wb.save(wb_path)
            if api_json:
                json_test_tables.append(api_json)

        json_path = os.path.join(outdir, f'test-array-{options["dbkey"]}.json')
        logger.info(f"Writing JSON to {json_path}")
        with open(json_path, "w") as test_file:
            jstr = json.dumps(json_test_tables, indent=2, sort_keys=True)
            test_file.write(jstr)
