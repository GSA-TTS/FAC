from collections import namedtuple as NT
from playhouse.shortcuts import model_to_dict
import os
import sys
import json

from django.core.management.base import BaseCommand

import argparse
import pprint

from audit.fixtures.workbooks.workbook_creation import (
    sections,
    workbook_loader,
    setup_sac,
)

import datetime

from audit.fixtures.census_models.census import (
    CensusGen22 as Gen,
)

import logging

pp = pprint.PrettyPrinter(indent=2)

parser = argparse.ArgumentParser()

logger = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

# This provides a way to map the sheet in the workbook to the
# column in the DB. It also has a default value and
# the type of value, so that things can be set correctly
# before filling in the XLSX workbooks.
FieldMap = NT("FieldMap", "in_sheet in_db default type")

# tools/workbook-generator/templates/additional-ueis-workbook.xlsx
# tools/workbook-generator/templates/audit-findings-text-workbook.xlsx
# tools/workbook-generator/templates/corrective-action-plan-workbook.xlsx
# tools/workbook-generator/templates/federal-awards-audit-findings-workbook.xlsx
# tools/workbook-generator/templates/federal-awards-workbook.xlsx
# tools/workbook-generator/templates/notes-to-sefa-workbook.xlsx
# tools/workbook-generator/templates/PLACE-TEMPLATE-FILES-HERE
# tools/workbook-generator/templates/secondary-auditors-workbook.xlsx

templates = {
    "AdditionalUEIs": "additional-ueis-workbook.xlsx",
    "AuditFindingsText": "audit-findings-text-workbook.xlsx",
    "CAP": "corrective-action-plan-workbook.xlsx",
    "AuditFindings": "federal-awards-audit-findings-workbook.xlsx",
    "FederalAwards": "federal-awards-workbook.xlsx",
    "SEFA": "notes-to-sefa-workbook.xlsx",
    "SecondaryAuditors": "secondary-auditors-workbook.xlsx",
}


def set_single_cell_range(wb, range_name, value):
    the_range = wb.defined_names[range_name]
    # The above returns a generator. Turn it to a list, and grab
    # the first element of the list. Now, this *tuple* contains a
    # sheet name and a cell reference... which you need to get rid
    # of the '$' to use.
    # https://itecnote.com/tecnote/python-using-excel-named-ranges-in-python-with-openpyxl/
    tup = list(the_range.destinations)[0]
    sheet_title = tup[0]
    cell_ref = tup[1].replace("$", "")
    ws = wb[sheet_title]
    ws[cell_ref] = value


# A tiny helper to index into workbooks.
# Assumes a capital letter.
def col_to_ndx(col):
    return ord(col) - 65 + 1


# Helper to set a range of values.
# Takes a named range, and then walks down the range,
# filling in values from the list past in (values).
def set_range(wb, range_name, values, default=None, type=str):
    the_range = wb.defined_names[range_name]
    dest = list(the_range.destinations)[0]
    sheet_title = dest[0]
    ws = wb[sheet_title]

    start_cell = dest[1].replace("$", "").split(":")[0]
    col = col_to_ndx(start_cell[0])
    start_row = int(start_cell[1])

    for ndx, v in enumerate(values):
        row = ndx + start_row
        if v:
            # This is a very noisy statement, showing everything
            # written into the workbook.
            # print(f'{range_name} c[{row}][{col}] <- {v} len({len(v)}) {default}')
            if v is not None:
                ws.cell(row=row, column=col, value=type(v))
            if len(v) == 0 and default is not None:
                # This is less noisy. Shows up for things like
                # empty findings counts. 2023 submissions
                # require that field to be 0, not empty,
                # if there are no findings.
                # print('Applying default')
                ws.cell(row=row, column=col, value=type(default))
        if not v:
            if default is not None:
                ws.cell(row=row, column=col, value=type(default))
            else:
                ws.cell(row=row, column=col, value="")
        else:
            # Leave it blank if we have no default passed in
            pass


def set_uei(wb, dbkey):
    g = Gen.select().where(Gen.dbkey == dbkey).get()
    set_single_cell_range(wb, "auditee_uei", g.uei)
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

    def handle(self, *args, **options):
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

        outdir = os.path.join(out_basedir, options["dbkey"])

        if not os.path.exists(outdir):
            try:
                os.mkdir(outdir)
                logger.info(f"Made directory {outdir}")
            except Exception as e:
                logger.info(e)
                logger.info("could not create output directory. exiting.")
                sys.exit()

        entity_id = "DBKEY {dbkey} {date:%Y_%m_%d_%H_%M_%S}".format(
            dbkey=options["dbkey"], date=datetime.datetime.now()
        )

        sac = setup_sac(None, entity_id, options["dbkey"])
        loader = workbook_loader(None, sac, options["dbkey"], entity_id)
        json_test_tables = []
        for section, fun in sections.items():
            (wb, api_json, filename) = loader(fun, section)
            wb_path = os.path.join(outdir, filename)
            wb.save(wb_path)
            json_test_tables.append(api_json)

        json_path = os.path.join(outdir, f'test-array-{options["dbkey"]}.json')
        logger.info(f"Writing JSON to {json_path}")
        with open(json_path, "w") as test_file:
            jstr = json.dumps(json_test_tables, indent=2, sort_keys=True)
            test_file.write(jstr)
