from audit.fixtures.workbooks.excel_creation import (
    FieldMap,
    templates,
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
    test_pfix
)

from audit.fixtures.census_models.ay22 import (
    CensusGen22 as Gen,
    CensusCpas22 as Cpas,
)

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    FieldMap('secondary_auditor_address_city', 'cpacity', None, str),
    FieldMap('secondary_auditor_contact_name', 'cpacontact', None, str),
    FieldMap('secondary_auditor_ein', 'cpaein', None, str),
    FieldMap('secondary_auditor_contact_email', 'cpaemail', None, str),
    FieldMap('secondary_auditor_name', 'cpafirmname', None, str),
    FieldMap('secondary_auditor_contact_phone', 'cpaphone', None, str),
    FieldMap('secondary_auditor_address_state', 'cpastate', None, str),
    FieldMap('secondary_auditor_address_street', 'cpastreet1', None, test_pfix(3)),
    FieldMap('secondary_auditor_contact_title', 'cpatitle', None, test_pfix(3)),
    FieldMap('secondary_auditor_address_zipcode', 'cpazipcode', None, str)
]

def generate_secondary_auditors(dbkey, outfile):
    logger.info(f"--- generate secondary auditors {dbkey} ---")
    wb = pyxl.load_workbook(templates["SecondaryAuditors"])

    g = set_uei(Gen, wb, dbkey)
    sec_cpas = Cpas.select().where(Cpas.dbkey == g.dbkey)
    
    map_simple_columns(wb, mappings, sec_cpas)
    wb.save(outfile)
    
    table = generate_dissemination_test_table(Gen, 'secondary_auditors', dbkey, mappings, sec_cpas)
    table['singletons']['auditee_uei'] = g.uei

    return (wb, table)

