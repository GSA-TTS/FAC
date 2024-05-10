from ..transforms.xform_retrieve_uei import xform_retrieve_uei
from ..transforms.xform_remove_hyphen_and_pad_zip import xform_remove_hyphen_and_pad_zip
from ..transforms.xform_string_to_string import string_to_string
from ..workbooklib.excel_creation_utils import (
    map_simple_columns,
    set_workbook_uei,
    sort_by_field,
    track_transformations,
)
from ..base_field_maps import SheetFieldMap
from ..workbooklib.templates import sections_to_template_paths
from ..models import ELECCPAS as Caps
from ..change_record import InspectionRecord
from audit.fixtures.excel import FORM_SECTIONS
from django.conf import settings
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


def xform_address_state(secondary_auditors):
    """Default missing address_state to GSA_MIGRATION"""
    change_records = []
    is_empty_address_state_found = False

    for secondary_auditor in secondary_auditors:
        address_state = string_to_string(secondary_auditor.CPASTATE)
        if not address_state:
            track_transformations(
                "CPASTATE",
                secondary_auditor.CPASTATE,
                "address_state",
                settings.GSA_MIGRATION,
                ["xform_address_state"],
                change_records,
            )

            is_empty_address_state_found = True
            secondary_auditor.CPASTATE = settings.GSA_MIGRATION

    if change_records and is_empty_address_state_found:
        InspectionRecord.append_secondary_auditor_changes(change_records)


def _get_secondary_auditors(dbkey, year):
    results = Caps.objects.filter(DBKEY=dbkey, AUDITYEAR=year)

    return sort_by_field(results, "ID")


def xform_cpafirmname(secondary_auditors):
    """NOTE: We track all secondary_auditors data in change_records.
    Save change_records in InspectionRecord only if at least one blank CPAFIRMNAME is found.
    We do this so that we can match changedrecord to record in dissemination table in a one on one fashion.
    """

    change_records = []
    is_empty_cpafirmname_found = False
    for secondary_auditor in secondary_auditors:
        cpafirmname = string_to_string(secondary_auditor.CPAFIRMNAME)
        if cpafirmname == "":
            is_empty_cpafirmname_found = True
            cpafirmname = settings.GSA_MIGRATION
        track_transformations(
            "CPAFIRMNAME",
            secondary_auditor.CPAFIRMNAME,
            "auditor_name",
            cpafirmname,
            ["xform_cpafirmname"],
            change_records,
        )
        secondary_auditor.CPAFIRMNAME = cpafirmname

    if change_records and is_empty_cpafirmname_found:
        InspectionRecord.append_secondary_auditor_changes(change_records)


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
    xform_address_state(secondary_auditors)
    xform_cpafirmname(secondary_auditors)
    map_simple_columns(wb, mappings, secondary_auditors)
    wb.save(outfile)

    return wb
