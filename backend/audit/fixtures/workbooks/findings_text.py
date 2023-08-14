from audit.fixtures.workbooks.excel_creation import (
    FieldMap,
    WorkbookFieldInDissem,
    templates,
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
    test_pfix
)

from audit.fixtures.census_models.ay22 import (
    CensusGen22 as Gen,
    CensusFindingstext22 as Findingstext
)
from audit.fixtures.workbooks.excel_creation import (
    insert_version_and_sheet_name
)
import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

def generate_findings_text(dbkey, outfile):
    logger.info(f"--- generate findings text {dbkey} ---")
    wb = pyxl.load_workbook(templates["AuditFindingsText"])
    mappings = [
        FieldMap('reference_number', 'findingrefnums', 'finding_ref_number', None, str),
        FieldMap('text_of_finding', 'text', 'finding_text', None, test_pfix(3)),
        FieldMap('contains_chart_or_table', 'chartstables', WorkbookFieldInDissem, None, str),
    ]
    g = set_uei(Gen, wb, dbkey)
    insert_version_and_sheet_name(wb, "audit-findings-text-workbook")

    ftexts = Findingstext.select().where(Findingstext.dbkey == g.dbkey)
    map_simple_columns(wb, mappings, ftexts)
    wb.save(outfile)
    table = generate_dissemination_test_table(Gen, 'finding_text', dbkey, mappings, ftexts)
    table['singletons']['auditee_uei'] = g.uei

    return (wb, table)
