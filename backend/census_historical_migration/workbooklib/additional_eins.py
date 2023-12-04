from ..transforms.xform_string_to_string import (
    string_to_string,
)
from ..workbooklib.excel_creation_utils import (
    get_audit_header,
    map_simple_columns,
    generate_dissemination_test_table,
    set_workbook_uei,
)
from ..base_field_maps import (
    SheetFieldMap,
    WorkbookFieldInDissem,
)
from ..workbooklib.templates import sections_to_template_paths
from ..models import ELECEINS as Eins
from audit.fixtures.excel import FORM_SECTIONS

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)


def xform_remove_trailing_decimal_zero(value):
    """
    Removes trailing .0 from a EIN strings.
    """
    trimmed_ein = string_to_string(value)
    if trimmed_ein.endswith(".0"):
        return trimmed_ein[:-2]
    return trimmed_ein


mappings = [
    SheetFieldMap(
        "additional_ein",
        "EIN",
        WorkbookFieldInDissem,
        None,
        xform_remove_trailing_decimal_zero,
    ),
]


def _get_eins(dbkey):
    return Eins.objects.filter(DBKEY=dbkey)


def generate_additional_eins(dbkey, year, outfile):
    """
    Generates additional eins workbook for a given dbkey.
    """
    logger.info(f"--- generate additional eins {dbkey} {year} ---")

    wb = pyxl.load_workbook(sections_to_template_paths[FORM_SECTIONS.ADDITIONAL_EINS])
    audit_header = get_audit_header(dbkey)

    set_workbook_uei(wb, audit_header.UEI)

    addl_eins = _get_eins(dbkey)
    map_simple_columns(wb, mappings, addl_eins)
    wb.save(outfile)
    # FIXME - MSHD: The logic below will most likely be removed, see comment in federal_awards.py
    table = generate_dissemination_test_table(
        audit_header, "additional_eins", dbkey, mappings, addl_eins
    )
    table["singletons"]["auditee_uei"] = audit_header.UEI
    return (wb, table)
