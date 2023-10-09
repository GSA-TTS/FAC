from dissemination.workbooklib.excel_creation import (
    FieldMap,
    WorkbookFieldInDissem,
    templates,
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
)


from dissemination.workbooklib.excel_creation import insert_version_and_sheet_name
from dissemination.workbooklib.census_models.census import dynamic_import

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    FieldMap("additional_ein", "ein", WorkbookFieldInDissem, None, str),
]


def generate_additional_eins(dbkey, year, outfile):
    logger.info(f"--- generate additional eins {dbkey} {year} ---")
    Gen = dynamic_import("Gen", year)
    Eins = dynamic_import("Eins", year)
    wb = pyxl.load_workbook(templates["AdditionalEINs"])

    g = set_uei(Gen, wb, dbkey)
    insert_version_and_sheet_name(wb, "additional-eins-workbook")

    addl_eins = Eins.select().where(Eins.dbkey == g.dbkey)
    map_simple_columns(wb, mappings, addl_eins)
    wb.save(outfile)

    table = generate_dissemination_test_table(
        Gen, "additional_eins", dbkey, mappings, addl_eins
    )
    table["singletons"]["auditee_uei"] = g.uei
    return (wb, table)
