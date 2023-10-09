from dissemination.workbooklib.excel_creation import (
    FieldMap,
    WorkbookFieldInDissem,
    templates,
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
    test_pfix,
)

from dissemination.workbooklib.excel_creation import insert_version_and_sheet_name
from dissemination.workbooklib.census_models.census import dynamic_import


import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)


def generate_corrective_action_plan(dbkey, year, outfile):
    logger.info(f"--- generate corrective action plan {dbkey} {year} ---")
    Gen = dynamic_import('Gen', year)
    Captext = dynamic_import('Captext', year)
    wb = pyxl.load_workbook(templates["CAP"])
    mappings = [
        FieldMap("reference_number", "findingrefnums", "finding_ref_number", None, str),
        FieldMap("planned_action", "text", WorkbookFieldInDissem, None, test_pfix(3)),
        FieldMap(
            "contains_chart_or_table", "chartstables", WorkbookFieldInDissem, None, str
        ),
    ]

    g = set_uei(Gen, wb, dbkey)
    insert_version_and_sheet_name(wb, "corrective-action-plan-workbook")

    captexts = Captext.select().where(Captext.dbkey == g.dbkey)

    map_simple_columns(wb, mappings, captexts)
    wb.save(outfile)

    table = generate_dissemination_test_table(
        Gen, "corrective_action_plans", dbkey, mappings, captexts
    )
    table["singletons"]["auditee_uei"] = g.uei

    return (wb, table)
