from census_historical_migration.workbooklib.excel_creation import (
    FieldMap,
    WorkbookFieldInDissem,
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
    test_pfix,
)
from census_historical_migration.workbooklib.templates import sections_to_template_paths
from census_historical_migration.workbooklib.census_models.census import dynamic_import


import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)


def generate_corrective_action_plan(dbkey, year, outfile):
    logger.info(f"--- generate corrective action plan {dbkey} {year} ---")
    Gen = dynamic_import("Gen", year)
    Captext = dynamic_import("Captext", year)
    wb = pyxl.load_workbook(sections_to_template_paths["CorrectiveActionPlan"])
    mappings = [
        FieldMap("reference_number", "findingrefnums", "finding_ref_number", None, str),
        FieldMap("planned_action", "text", WorkbookFieldInDissem, None, test_pfix(3)),
        FieldMap(
            "contains_chart_or_table", "chartstables", WorkbookFieldInDissem, None, str
        ),
    ]

    g = set_uei(Gen, wb, dbkey)

    captexts = Captext.select().where(Captext.dbkey == g.dbkey)

    map_simple_columns(wb, mappings, captexts)
    wb.save(outfile)

    table = generate_dissemination_test_table(
        Gen, "corrective_action_plans", dbkey, mappings, captexts
    )
    table["singletons"]["auditee_uei"] = g.uei

    return (wb, table)
