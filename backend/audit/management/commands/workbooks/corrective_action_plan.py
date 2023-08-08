from audit.management.commands.workbooks.excel_creation import (
    FieldMap,
    templates,
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
)

from audit.management.commands.census_models.ay22 import (
    CensusGen22 as Gen,
    CensusCaptext22 as Captext
)

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)
def generate_corrective_action_plan(dbkey, outfile):
    print("--- generate corrective action plan ---")
    wb = pyxl.load_workbook(templates["CAP"])
    mappings = [
        FieldMap('reference_number', 'findingrefnums', None, str),
        FieldMap('planned_action', 'text', None, str),
        FieldMap('contains_chart_or_table', 'chartstables', None, str)
    ]
    
    g = set_uei(Gen, wb, dbkey)
    captexts = Captext.select().where(Captext.dbkey == g.dbkey)
    
    map_simple_columns(wb, mappings, captexts)
    wb.save(outfile)

    table = generate_dissemination_test_table(Gen, 'cap_text', dbkey, mappings, captexts)
    table['singletons']['auditee_uei'] = g.uei

    return (wb, table)
