from ..transforms.xform_retrieve_uei import xform_retrieve_uei
from ..transforms.xform_remove_hyphen_and_pad_zip import xform_remove_hyphen_and_pad_zip
from ..workbooklib.excel_creation_utils import (
    map_simple_columns,
    set_workbook_uei,
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
        xform_remove_hyphen_and_pad_zip,
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
    uei = xform_retrieve_uei(audit_header.UEI)
    set_workbook_uei(wb, uei)
    secondary_auditors = _get_secondary_auditors(
        audit_header.DBKEY, audit_header.AUDITYEAR
    )
    map_simple_columns(wb, mappings, secondary_auditors)
    wb.save(outfile)

    return wb
