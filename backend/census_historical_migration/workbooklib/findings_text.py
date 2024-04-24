from django.conf import settings
from ..workbooklib.findings import get_findings
from ..transforms.xform_retrieve_uei import xform_retrieve_uei
from ..workbooklib.excel_creation_utils import (
    get_reference_numbers_from_findings,
    get_reference_numbers_from_text_records,
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


def xform_add_placeholder_for_missing_references(findings, findings_texts):
    """
    Add placeholder for missing finding reference numbers.
    """

    expected_references = get_reference_numbers_from_findings(findings)
    found_references = get_reference_numbers_from_text_records(findings_texts)

    missing_references = expected_references - found_references

    if missing_references:
        for ref in missing_references:
            findings_texts.append(
                FindingsText(
                    SEQ_NUMBER="0",
                    FINDINGREFNUMS=ref,
                    TEXT=settings.GSA_MIGRATION,
                    CHARTSTABLES=settings.GSA_MIGRATION,
                )
            )

    return findings_texts


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
    findings = get_findings(audit_header.DBKEY, audit_header.AUDITYEAR)
    findings_texts = _get_findings_texts(audit_header.DBKEY, audit_header.AUDITYEAR)
    findings_texts = xform_add_placeholder_for_missing_references(
        findings, findings_texts
    )
    xform_sanitize_for_excel(findings_texts)
    map_simple_columns(wb, mappings, findings_texts)

    wb.save(outfile)

    return wb
