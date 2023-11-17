from census_historical_migration.base_field_maps import WorkbookFieldInDissem
from census_historical_migration.sac_general_lib.report_id_generator import (
    dbkey_to_report_id,
)
from openpyxl.utils.cell import column_index_from_string
from playhouse.shortcuts import model_to_dict

import sys
import logging


logger = logging.getLogger(__name__)


# Helper to set a range of values.
# Takes a named range, and then walks down the range,
# filling in values from the list past in (values).
def set_range(wb, range_name, values, default=None, conversion_fun=str):
    the_range = wb.defined_names[range_name]
    dest = list(the_range.destinations)[0]
    sheet_title = dest[0]
    ws = wb[sheet_title]

    start_cell = dest[1].replace("$", "").split(":")[0]
    col = column_index_from_string(start_cell[0])
    start_row = int(start_cell[1])

    for ndx, v in enumerate(values):
        row = ndx + start_row
        if v:
            # This is a very noisy statement, showing everything
            # written into the workbook.
            # print(f'{range_name} c[{row}][{col}] <- {type(v)} len({len(v)}) {default}')
            if v is not None:
                ws.cell(row=row, column=col, value=conversion_fun(v))
            if len(str(v)) == 0 and default is not None:
                # This is less noisy. Shows up for things like
                # empty findings counts. 2023 submissions
                # require that field to be 0, not empty,
                # if there are no findings.
                # print('Applying default')
                ws.cell(row=row, column=col, value=conversion_fun(default))
        if not v:
            if default is not None:
                ws.cell(row=row, column=col, value=conversion_fun(default))
            else:
                ws.cell(row=row, column=col, value="")
        else:
            # Leave it blank if we have no default passed in
            pass


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


def add_hyphen_to_zip(zip):
    strzip = str(zip)
    if len(strzip) == 5:
        return strzip
    elif len(strzip) == 9:
        return f"{strzip[0:5]}-{strzip[5:9]}"
    else:
        logger.info("ZIP IS MALFORMED IN WORKBOOKS E2E / SAC_CREATION")
        return strzip


def generate_dissemination_test_table(Gen, api_endpoint, dbkey, mappings, objects):
    table = {"rows": list(), "singletons": dict()}
    table["endpoint"] = api_endpoint
    table["report_id"] = dbkey_to_report_id(Gen, dbkey)
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
