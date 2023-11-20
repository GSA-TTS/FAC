from playhouse.shortcuts import model_to_dict

from collections import namedtuple as NT
from openpyxl.utils.cell import rows_from_range, coordinate_from_string
from openpyxl.utils.cell import column_index_from_string

from datetime import date
from config import settings
import logging
import sys
import json


logger = logging.getLogger(__name__)

# This provides a way to map the sheet in the workbook to the
# column in the DB. It also has a default value and
# the type of value, so that things can be set correctly
# before filling in the XLSX workbooks.
FieldMap = NT("FieldMap", "in_sheet in_db in_dissem default type")
WorkbookFieldInDissem = 1000


def set_range(wb, range_name, values, default=None, conversion_fun=str):
    """
    Helper to set a range of values. Takes a named range, and then walks down
    the range, filling in the given values.

    wb (Workbook)       The workbook
    range_name (string) Name of the range to set
    values (iterable)   Values to set within the range
    default (any)       Default value to use; defaults to None.
    conversion (func)   Conversion function to apply to individual values; defaults to str().
    """
    the_range = wb.defined_names[range_name]
    dests = the_range.destinations

    sheet_title, coord = None, None
    for s, c in dests:
        if sheet_title or coord:
            # `destinations` is meant to be iterated over, but we only expect one value
            raise ValueError(f"{range_name} has more than one destination")
        else:
            sheet_title, coord = s, c

    ws = None
    try:
        ws = wb[sheet_title]
    except KeyError:
        raise KeyError(f"Sheet title '{sheet_title}' not found in workbook")

    values = list(values)
    for i, row in enumerate(rows_from_range(coord)):
        # Iterate over the rows, but stop when we run out of values
        value = None
        try:
            value = values[i]
        except IndexError:
            break

        # Get the row and column to set the current value
        cell = row[0]                               # [('B12',)] -> ('B12',)
        col_str, row = coordinate_from_string(cell) # ('B12',) -> 'B', 12
        col = column_index_from_string(col_str)     # 'B' -> 2

        # Set the value of the cell
        converted_value = conversion_fun(value) if value else default or ""
        ws.cell(row=row, column=col, value=converted_value)


def set_uei(Gen, wb, dbkey):
    g = Gen.select().where(Gen.dbkey == dbkey).get()
    if g.uei:
        set_range(wb, "auditee_uei", [g.uei])
    else:
        g.uei = "BADBADBADBAD"
        set_range(wb, "auditee_uei", [g.uei])
    return g


def map_simple_columns(wb, mappings, values):
    len_passed_in = len(mappings)
    unique_fields = set()
    for mapping in mappings:
        unique_fields.add(mapping.in_sheet)
    if len_passed_in != len(unique_fields):
        logger.info(f"unique: {len(unique_fields)} list: {len(mappings)}")
        logger.error(
            "You repeated a field in the mappings: {}".format(
                list(map(lambda m: m.in_sheet, mappings))
            )
        )
        sys.exit(-1)

    # Map all the simple ones
    for m in mappings:
        set_range(
            wb,
            m.in_sheet,
            map(lambda v: model_to_dict(v)[m.in_db], values),
            m.default,
            m.type,
        )


def _census_date_to_datetime(cd):
    lookup = {
        "JAN": 1,
        "FEB": 2,
        "MAR": 3,
        "APR": 4,
        "MAY": 5,
        "JUN": 6,
        "JUL": 7,
        "AUG": 8,
        "SEP": 9,
        "OCT": 10,
        "NOV": 11,
        "DEC": 12,
    }
    year = int(cd.split("-")[2])
    month = lookup[cd.split("-")[1]]
    day = int(cd.split("-")[0])
    return date(year + 2000, month, day)


# FIXME: Get the padding/shape right on the report_id
def dbkey_to_test_report_id(Gen, dbkey):
    g = Gen.select(Gen.audityear, Gen.fyenddate).where(Gen.dbkey == dbkey).get()
    # month = g.fyenddate.split('-')[1]
    # 2022JUN0001000003
    # We start new audits at 1 million.
    # So, we want 10 digits, and zero-pad for
    # historic DBKEY report_ids
    dt = _census_date_to_datetime(g.fyenddate)
    return f"{g.audityear}-{dt.month:02}-TSTDAT-{dbkey.zfill(10)}"


def generate_dissemination_test_table(Gen, api_endpoint, dbkey, mappings, objects):
    table = {"rows": list(), "singletons": dict()}
    table["endpoint"] = api_endpoint
    table["report_id"] = dbkey_to_test_report_id(Gen, dbkey)
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
                if m.in_dissem == WorkbookFieldInDissem:
                    # print(f'in_sheet {m.in_sheet} <- {as_dict[m.in_db]}')
                    test_obj["fields"].append(m.in_sheet)
                    # The typing must be applied here as well, as in the case of
                    # type_requirement, it alphabetizes the value...
                    test_obj["values"].append(m.type(as_dict[m.in_db]))
                else:
                    # print(f'in_dissem {m.in_dissem} <- {as_dict[m.in_db]}')
                    test_obj["fields"].append(m.in_dissem)
                    test_obj["values"].append(m.type(as_dict[m.in_db]))

        table["rows"].append(test_obj)
    return table


def extract_metadata(sheet_json, range):
    excel_defn = open(
        f"{settings.BASE_DIR}/schemas/output/excel/json/{sheet_json}.json"
    )
    excel_defn_json = json.load(excel_defn)
    result = None
    for sheet in excel_defn_json["sheets"]:
        if "name" in sheet and sheet["name"] == "Coversheet":
            coversheet = sheet
            for scell in coversheet["single_cells"]:
                if ("range_name" in scell) and (scell["range_name"] == range):
                    result = scell["value"]
    return result
