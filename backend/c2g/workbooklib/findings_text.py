from .excel_creation import (
    FieldMap,
    WorkbookFieldInDissem,
    templates,
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
    test_pfix,
)

from .excel_creation import insert_version_and_sheet_name
from audit.models import SingleAuditChecklist
from c2g.models import (
    ELECFINDINGSTEXT as FTexts,
)

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    FieldMap(
        "reference_number", "findingrefnums".upper(), "finding_ref_number", None, str
    ),
    FieldMap("text_of_finding", "text".upper(), "finding_text", None, test_pfix(3)),
    FieldMap(
        "contains_chart_or_table",
        "chartstables".upper(),
        WorkbookFieldInDissem,
        None,
        str,
    ),
]


def generate_findings_text(sac: SingleAuditChecklist, dbkey, audit_year, outfile):
    logger.info(f"--- generate findings text {dbkey} {audit_year} ---")
    wb = pyxl.load_workbook(templates["AuditFindingsText"])

    set_uei(sac, wb)
    insert_version_and_sheet_name(wb, "audit-findings-text-workbook")

    ftexts = FTexts.objects.filter(DBKEY=dbkey, AUDITYEAR=audit_year)
    map_simple_columns(wb, mappings, ftexts)
    wb.save(outfile)
    table = generate_dissemination_test_table(
        sac, "findings_text", audit_year, dbkey, mappings, ftexts
    )
    table["singletons"]["auditee_uei"] = sac.auditee_uei

    return (wb, table)
