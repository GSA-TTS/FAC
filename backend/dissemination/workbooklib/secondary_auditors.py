from dissemination.workbooklib.excel_creation import (
    FieldMap,
    templates,
    set_uei,
    map_simple_columns,
    generate_dissemination_test_table,
    test_pfix,
)

from dissemination.workbooklib.census_models.census import dynamic_import


from dissemination.workbooklib.sac_creation import add_hyphen_to_zip

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    FieldMap("secondary_auditor_address_city", "cpacity", "address_city", None, str),
    FieldMap("secondary_auditor_contact_name", "cpacontact", "contact_name", None, str),
    FieldMap("secondary_auditor_ein", "cpaein", "auditor_ein", None, str),
    FieldMap("secondary_auditor_contact_email", "cpaemail", "contact_email", None, str),
    FieldMap("secondary_auditor_name", "cpafirmname", "auditor_name", None, str),
    FieldMap("secondary_auditor_contact_phone", "cpaphone", "contact_phone", None, str),
    FieldMap("secondary_auditor_address_state", "cpastate", "address_state", None, str),
    FieldMap(
        "secondary_auditor_address_street",
        "cpastreet1",
        "address_street",
        None,
        test_pfix(3),
    ),
    FieldMap(
        "secondary_auditor_contact_title",
        "cpatitle",
        "contact_title",
        None,
        test_pfix(3),
    ),
    FieldMap(
        "secondary_auditor_address_zipcode",
        "cpazipcode",
        "address_zipcode",
        None,
        add_hyphen_to_zip,
    ),
]


def generate_secondary_auditors(dbkey, year, outfile):
    logger.info(f"--- generate secondary auditors {dbkey} {year} ---")
    Gen = dynamic_import("Gen", year)
    Cpas = dynamic_import("Cpas", year)
    wb = pyxl.load_workbook(templates["SecondaryAuditors"])

    g = set_uei(Gen, wb, dbkey)

    sec_cpas = Cpas.select().where(Cpas.dbkey == g.dbkey)

    map_simple_columns(wb, mappings, sec_cpas)

    wb.save(outfile)

    table = generate_dissemination_test_table(
        Gen, "secondary_auditor", dbkey, mappings, sec_cpas
    )

    table["singletons"]["auditee_uei"] = g.uei

    return (wb, table)
