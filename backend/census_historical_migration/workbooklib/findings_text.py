from census_historical_migration.workbooklib.excel_creation_utils import (
    get_audit_header,
    map_simple_columns,
    generate_dissemination_test_table,
    set_workbook_uei,
)
from census_historical_migration.base_field_maps import (
    SheetFieldMap,
    WorkbookFieldInDissem,
)
from census_historical_migration.workbooklib.templates import sections_to_template_paths
from census_historical_migration.models import ELECFINDINGSTEXT as FindingsText
from audit.fixtures.excel import FORM_SECTIONS

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    SheetFieldMap(
        "reference_number", "FINDINGREFNUMS", "finding_ref_number", None, str
    ),
    SheetFieldMap("text_of_finding", "TEXT", "finding_text", None, str),
    SheetFieldMap(
        "contains_chart_or_table", "CHARTSTABLES", WorkbookFieldInDissem, None, str
    ),
]


def _get_findings_text(dbkey):
    return FindingsText.objects.filter(DBKEY=dbkey).order_by("SEQ_NUMBER")


def generate_findings_text(dbkey, year, outfile):
    """
    Generates a findings text workbook for a given dbkey.

    Note: This function assumes that all the findings text
    information in the database is related to the same year.
    """
    logger.info(f"--- generate findings text {dbkey} {year} ---")

    wb = pyxl.load_workbook(sections_to_template_paths[FORM_SECTIONS.FINDINGS_TEXT])

    audit_header = get_audit_header(dbkey)

    set_workbook_uei(wb, audit_header.UEI)

    findings_texts = _get_findings_text(dbkey)

    map_simple_columns(wb, mappings, findings_texts)

    wb.save(outfile)

    table = generate_dissemination_test_table(
        audit_header, "findings_text", dbkey, mappings, findings_texts
    )
    table["singletons"]["auditee_uei"] = audit_header.UEI

    return (wb, table)
