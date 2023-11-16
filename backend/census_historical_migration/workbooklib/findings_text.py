from census_historical_migration.workbooklib.excel_creation import (
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
)
from census_historical_migration.base_field_maps import (
    SheetFieldMap,
    WorkbookFieldInDissem,
)
from census_historical_migration.workbooklib.templates import sections_to_template_paths
from census_historical_migration.workbooklib.census_models.census import dynamic_import
from audit.fixtures.excel import FORM_SECTIONS

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    SheetFieldMap(
        "reference_number", "findingrefnums", "finding_ref_number", None, str
    ),
    SheetFieldMap("text_of_finding", "text", "finding_text", None, str),
    SheetFieldMap(
        "contains_chart_or_table", "chartstables", WorkbookFieldInDissem, None, str
    ),
]


def generate_findings_text(dbkey, year, outfile):
    logger.info(f"--- generate findings text {dbkey} {year} ---")
    Gen = dynamic_import("Gen", year)
    Findingstext = dynamic_import("Findingstext", year)
    wb = pyxl.load_workbook(sections_to_template_paths[FORM_SECTIONS.FINDINGS_TEXT])

    g = set_uei(Gen, wb, dbkey)

    ftexts = Findingstext.select().where(Findingstext.dbkey == g.dbkey)
    map_simple_columns(wb, mappings, ftexts)
    wb.save(outfile)
    table = generate_dissemination_test_table(
        Gen, "findings_text", dbkey, mappings, ftexts
    )
    table["singletons"]["auditee_uei"] = g.uei

    return (wb, table)
