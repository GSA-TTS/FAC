from ..transforms.xform_retrieve_uei import xform_retrieve_uei
from ..workbooklib.excel_creation_utils import (
    map_simple_columns,
    set_workbook_uei,
    sort_by_field,
    xform_sanitize_for_excel,
)
from ..base_field_maps import (
    SheetFieldMap,
    WorkbookFieldInDissem,
)
from ..workbooklib.templates import sections_to_template_paths
from ..models import ELECFINDINGSTEXT as FindingsText
from audit.fixtures.excel import FORM_SECTIONS

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    SheetFieldMap(
        "reference_number", "FINDINGREFNUMS", "finding_ref_number", None, str
    ),
    SheetFieldMap("text_of_finding", "TEXT", "finding_text", None, str),
    SheetFieldMap(
        "contains_chart_or_table", "CHARTSTABLES", WorkbookFieldInDissem, None, str
    ),
]


def _get_findings_texts(dbkey, year):
    results = FindingsText.objects.filter(DBKEY=dbkey, AUDITYEAR=year)
    return sort_by_field(results, "SEQ_NUMBER")


def generate_findings_text(audit_header, outfile):
    """
    Generates a findings text workbook for a given audit header.
    """
    logger.info(
        f"--- generate findings text {audit_header.DBKEY} {audit_header.AUDITYEAR} ---"
    )

    wb = pyxl.load_workbook(sections_to_template_paths[FORM_SECTIONS.FINDINGS_TEXT])
    uei = xform_retrieve_uei(audit_header.UEI)
    set_workbook_uei(wb, uei)

    findings_texts = _get_findings_texts(audit_header.DBKEY, audit_header.AUDITYEAR)
    xform_sanitize_for_excel(findings_texts)
    map_simple_columns(wb, mappings, findings_texts)

    wb.save(outfile)

    return wb
