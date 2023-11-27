from census_historical_migration.workbooklib.excel_creation_utils import (
    get_audit_header,
    map_simple_columns,
    generate_dissemination_test_table,
    set_workbook_uei,
)
from census_historical_migration.base_field_maps import (
    SheetFieldMap,
    WorkbookFieldInDissem,
)
from census_historical_migration.workbooklib.templates import sections_to_template_paths
from census_historical_migration.models import ELECUEIS as Ueis
from audit.fixtures.excel import FORM_SECTIONS

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    # FIXME: We have no dissemination nodel for this.
    SheetFieldMap("additional_uei", "UEI", WorkbookFieldInDissem, None, str),
]


def _get_ueis(dbkey):
    return Ueis.objects.filter(DBKEY=dbkey)


def generate_additional_ueis(dbkey, year, outfile):
    """
    Generates additional ueis workbook for a given dbkey.
    """
    logger.info(f"--- generate additional ueis {dbkey} {year} ---")

    wb = pyxl.load_workbook(sections_to_template_paths[FORM_SECTIONS.ADDITIONAL_UEIS])
    audit_header = get_audit_header(dbkey)

    set_workbook_uei(wb, audit_header.UEI)

    additional_ueis = _get_ueis(dbkey)
    map_simple_columns(wb, mappings, additional_ueis)
    wb.save(outfile)

    # FIXME - MSHD: The logic below will most likely be removed, see comment in federal_awards.py
    table = generate_dissemination_test_table(
        audit_header, "additional_ueis", dbkey, mappings, additional_ueis
    )

    table["singletons"]["auditee_uei"] = audit_header.UEI
    return (wb, table)
