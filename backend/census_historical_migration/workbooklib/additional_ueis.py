from census_historical_migration.workbooklib.excel_creation import (
    FieldMap,
    WorkbookFieldInDissem,
    templates,
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
)


from census_historical_migration.workbooklib.census_models.census import dynamic_import

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    # FIXME: We have no dissemination nodel for this.
    FieldMap("additional_uei", "uei", WorkbookFieldInDissem, None, str),
]


def generate_additional_ueis(dbkey, year, outfile):
    logger.info(f"--- generate additional ueis {dbkey} {year} ---")
    Gen = dynamic_import("Gen", year)
    wb = pyxl.load_workbook(templates["AdditionalUEIs"])
    g = set_uei(Gen, wb, dbkey)
    if int(year) >= 22:
        Ueis = dynamic_import("Ueis", year)
        addl_ueis = Ueis.select().where(Ueis.dbkey == g.dbkey)
        map_simple_columns(wb, mappings, addl_ueis)

        table = generate_dissemination_test_table(
            Gen, "additional_ueis", dbkey, mappings, addl_ueis
        )
    else:
        table = {}
        table["singletons"] = {}
    wb.save(outfile)
    table["singletons"]["auditee_uei"] = g.uei
    return (wb, table)
