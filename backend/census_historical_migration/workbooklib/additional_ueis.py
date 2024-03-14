from ..transforms.xform_retrieve_uei import xform_retrieve_uei
from ..workbooklib.excel_creation_utils import (
    map_simple_columns,
    set_workbook_uei,
    sort_by_field,
)
from ..base_field_maps import (
    SheetFieldMap,
    WorkbookFieldInDissem,
)
from ..workbooklib.templates import sections_to_template_paths
from ..models import ELECUEIS as Ueis
from audit.fixtures.excel import FORM_SECTIONS

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    SheetFieldMap("additional_uei", "UEI", WorkbookFieldInDissem, None, str),
]


def get_ueis(dbkey, year):
    results = Ueis.objects.filter(DBKEY=dbkey, AUDITYEAR=year).exclude(UEI="")

    return sort_by_field(results, "SEQNUM")


def generate_additional_ueis(audit_header, outfile):
    """
    Generates additional ueis workbook for a given audit header.
    """
    logger.info(
        f"--- generate additional ueis {audit_header.DBKEY} {audit_header.AUDITYEAR} ---"
    )
    uei = xform_retrieve_uei(audit_header.UEI)
    wb = pyxl.load_workbook(sections_to_template_paths[FORM_SECTIONS.ADDITIONAL_UEIS])
    set_workbook_uei(wb, uei)
    additional_ueis = get_ueis(audit_header.DBKEY, audit_header.AUDITYEAR)
    map_simple_columns(wb, mappings, additional_ueis)
    wb.save(outfile)

    return wb
