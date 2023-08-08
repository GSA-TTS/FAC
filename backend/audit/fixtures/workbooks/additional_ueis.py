from audit.fixtures.workbooks.excel_creation import (
    FieldMap,
    templates,
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
)

from audit.fixtures.census_models.ay22 import (
    CensusGen22 as Gen,
    CensusUeis22 as Ueis,
)

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    FieldMap('additional_uei', 'uei', None, str),
    #FieldMap('ueiseqnum', 'ueiseqnum', 0, int)
]

def generate_additional_ueis(dbkey, outfile):
    logger.info(f"--- generate additional ueis {dbkey} ---")
    wb = pyxl.load_workbook(templates["AdditionalUEIs"])

    g = set_uei(Gen, wb, dbkey)
    addl_ueis = Ueis.select().where(Ueis.dbkey == g.dbkey)
    map_simple_columns(wb, mappings, addl_ueis)
    wb.save(outfile)
    table = generate_dissemination_test_table(Gen, 'additional_ueis', dbkey, mappings, addl_ueis)
    table['singletons']['auditee_uei'] = g.uei

    return (wb, table)
