from ..transforms.xform_string_to_string import string_to_string
from ..workbooklib.excel_creation_utils import (
    map_simple_columns,
    generate_dissemination_test_table,
    set_workbook_uei,
    xform_add_hyphen_to_zip,
)
from ..base_field_maps import SheetFieldMap
from ..workbooklib.templates import sections_to_template_paths
from ..models import ELECCPAS as Caps
from audit.fixtures.excel import FORM_SECTIONS

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)


mappings = [
    SheetFieldMap(
        "secondary_auditor_address_city", "CPACITY", "address_city", None, str
    ),
    SheetFieldMap(
        "secondary_auditor_contact_name", "CPACONTACT", "contact_name", None, str
    ),
    SheetFieldMap("secondary_auditor_ein", "CPAEIN", "auditor_ein", None, str),
    SheetFieldMap(
        "secondary_auditor_contact_email", "CPAEMAIL", "contact_email", None, str
    ),
    SheetFieldMap("secondary_auditor_name", "CPAFIRMNAME", "auditor_name", None, str),
    SheetFieldMap(
        "secondary_auditor_contact_phone", "CPAPHONE", "contact_phone", None, str
    ),
    SheetFieldMap(
        "secondary_auditor_address_state", "CPASTATE", "address_state", None, str
    ),
    SheetFieldMap(
        "secondary_auditor_address_street",
        "CPASTREET1",
        "address_street",
        None,
        str,
    ),
    SheetFieldMap(
        "secondary_auditor_contact_title",
        "CPATITLE",
        "contact_title",
        None,
        str,
    ),
    SheetFieldMap(
        "secondary_auditor_address_zipcode",
        "CPAZIPCODE",
        "address_zipcode",
        None,
        xform_add_hyphen_to_zip,
    ),
]


def _get_secondary_auditors(dbkey, year):
    return Caps.objects.filter(DBKEY=dbkey, AUDITYEAR=year)


def generate_secondary_auditors(audit_header, outfile):
    """
    Generates secondary auditor workbook for a given audit header.
    """
    logger.info(
        f"--- generate secondary auditors {audit_header.DBKEY} {audit_header.AUDITYEAR} ---"
    )

    wb = pyxl.load_workbook(
        sections_to_template_paths[FORM_SECTIONS.SECONDARY_AUDITORS]
    )
    uei = string_to_string(audit_header.UEI)
    set_workbook_uei(wb, uei)
    secondary_auditors = _get_secondary_auditors(
        audit_header.DBKEY, audit_header.AUDITYEAR
    )
    map_simple_columns(wb, mappings, secondary_auditors)
    wb.save(outfile)

    table = generate_dissemination_test_table(
        audit_header, "secondary_auditors", mappings, secondary_auditors
    )
    table["singletons"]["auditee_uei"] = uei

    return (wb, table)
