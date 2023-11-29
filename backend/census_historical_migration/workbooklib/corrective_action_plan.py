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
from census_historical_migration.models import ELECCAPTEXT as CapText
from audit.fixtures.excel import FORM_SECTIONS


import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    SheetFieldMap(
        "reference_number", "FINDINGREFNUMS", "finding_ref_number", None, str
    ),
    SheetFieldMap("planned_action", "TEXT", WorkbookFieldInDissem, None, str),
    SheetFieldMap(
        "contains_chart_or_table", "CHARTSTABLES", WorkbookFieldInDissem, None, str
    ),
]


def _get_cap_text(dbkey):
    return CapText.objects.filter(DBKEY=dbkey).order_by("SEQ_NUMBER")


def generate_corrective_action_plan(dbkey, year, outfile):
    """
    Generates a corrective action plan workbook for a given dbkey.
    """
    logger.info(f"--- generate corrective action plan {dbkey} {year} ---")

    wb = pyxl.load_workbook(
        sections_to_template_paths[FORM_SECTIONS.CORRECTIVE_ACTION_PLAN]
    )
    audit_header = get_audit_header(dbkey)

    set_workbook_uei(wb, audit_header.UEI)

    captexts = _get_cap_text(dbkey)

    map_simple_columns(wb, mappings, captexts)
    wb.save(outfile)

    table = generate_dissemination_test_table(
        audit_header, "corrective_action_plans", dbkey, mappings, captexts
    )
    table["singletons"]["auditee_uei"] = audit_header.UEI

    return (wb, table)
