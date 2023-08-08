from audit.management.commands.workbooks.excel_creation import (
    FieldMap,
    templates,
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
)

from audit.management.commands.census_models.ay22 import (
    CensusGen22 as Gen,
    CensusFindingstext22 as Findingstext
)

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

def generate_findings_text(dbkey, outfile):
    logger.info(f"--- generate findings text {dbkey} ---")
    wb = pyxl.load_workbook(templates["AuditFindingsText"])
    mappings = [
        FieldMap('reference_number', 'findingrefnums', None, str),
        FieldMap('text_of_finding', 'text', None, str),
        FieldMap('contains_chart_or_table', 'chartstables', None, str),
    ]
    g = set_uei(Gen, wb, dbkey)
    ftexts = Findingstext.select().where(Findingstext.dbkey == g.dbkey)
    map_simple_columns(wb, mappings, ftexts)
    wb.save(outfile)
    table = generate_dissemination_test_table(Gen, 'findings_text', dbkey, mappings, ftexts)
    table['singletons']['auditee_uei'] = g.uei

    return (wb, table)
