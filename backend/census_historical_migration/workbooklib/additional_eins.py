from census_historical_migration.workbooklib.excel_creation import (
    WorkbookFieldInDissem,
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
)
from census_historical_migration.base_field_maps import SheetFieldMap
from census_historical_migration.workbooklib.templates import sections_to_template_paths
from census_historical_migration.workbooklib.census_models.census import dynamic_import
from audit.fixtures.excel import FORM_SECTIONS

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    SheetFieldMap("additional_ein", "ein", WorkbookFieldInDissem, None, str),
]


def generate_additional_eins(dbkey, year, outfile):
    logger.info(f"--- generate additional eins {dbkey} {year} ---")
    Gen = dynamic_import("Gen", year)
    Eins = dynamic_import("Eins", year)
    wb = pyxl.load_workbook(sections_to_template_paths[FORM_SECTIONS.ADDITIONAL_EINS])

    g = set_uei(Gen, wb, dbkey)

    addl_eins = Eins.select().where(Eins.dbkey == g.dbkey)
    map_simple_columns(wb, mappings, addl_eins)
    wb.save(outfile)

    table = generate_dissemination_test_table(
        Gen, "additional_eins", dbkey, mappings, addl_eins
    )
    table["singletons"]["auditee_uei"] = g.uei
    return (wb, table)
