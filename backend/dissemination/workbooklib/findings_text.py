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

mappings = [
    FieldMap("reference_number", "findingrefnums", "finding_ref_number", None, str),
    FieldMap("text_of_finding", "text", "finding_text", None, test_pfix(3)),
    FieldMap(
        "contains_chart_or_table", "chartstables", WorkbookFieldInDissem, None, str
    ),
]


def generate_findings_text(dbkey, year, outfile):
    logger.info(f"--- generate findings text {dbkey} {year} ---")
    Gen = dynamic_import("Gen", year)
    Findingstext = dynamic_import("Findingstext", year)
    wb = pyxl.load_workbook(templates["AuditFindingsText"])

    g = set_uei(Gen, wb, dbkey)
    insert_version_and_sheet_name(wb, "audit-findings-text-workbook")

    ftexts = Findingstext.select().where(Findingstext.dbkey == g.dbkey)
    map_simple_columns(wb, mappings, ftexts)
    wb.save(outfile)
    table = generate_dissemination_test_table(
        Gen, "findings_text", dbkey, mappings, ftexts
    )
    table["singletons"]["auditee_uei"] = g.uei

    return (wb, table)
