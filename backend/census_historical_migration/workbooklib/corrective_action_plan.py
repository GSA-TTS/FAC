from django.conf import settings

from ..transforms.xform_string_to_string import string_to_string

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
from ..models import ELECCAPTEXT as CapText
from audit.fixtures.excel import FORM_SECTIONS


import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    SheetFieldMap(
        "reference_number", "FINDINGREFNUMS", "finding_ref_number", None, str
    ),
    SheetFieldMap("planned_action", "TEXT", WorkbookFieldInDissem, None, str),
    SheetFieldMap(
        "contains_chart_or_table", "CHARTSTABLES", WorkbookFieldInDissem, None, str
    ),
]


def _get_cap_text(dbkey, year):
    results = CapText.objects.filter(DBKEY=dbkey, AUDITYEAR=year)

    return sort_by_field(results, "SEQ_NUMBER")


def xform_add_placeholder_for_missing_references(findings, captexts):
    """
    Add placeholder for missing finding reference numbers.
    """

    expected_references = get_reference_numbers_from_findings(findings)
    found_references = get_reference_numbers_from_text_records(captexts)

    missing_references = expected_references - found_references

    if missing_references:
        for ref in missing_references:
            captexts.append(
                CapText(
                    SEQ_NUMBER="0",
                    FINDINGREFNUMS=ref,
                    TEXT=settings.GSA_MIGRATION,
                    CHARTSTABLES=settings.GSA_MIGRATION,
                )
            )

    return captexts


def xform_add_placeholder_for_missing_action_planned(captexts):
    """
    Add placeholder for missing planned actions.
    """
    for captext in captexts:
        if string_to_string(captext.FINDINGREFNUMS) and not string_to_string(
            captext.TEXT
        ):
            captext.TEXT = settings.GSA_MIGRATION


def generate_corrective_action_plan(audit_header, outfile):
    """
    Generates a corrective action plan workbook for a given audit header.
    """
    logger.info(
        f"--- generate corrective action plan {audit_header.DBKEY} {audit_header.AUDITYEAR} ---"
    )

    uei = xform_retrieve_uei(audit_header.UEI)
    wb = pyxl.load_workbook(
        sections_to_template_paths[FORM_SECTIONS.CORRECTIVE_ACTION_PLAN]
    )
    set_workbook_uei(wb, uei)
    captexts = _get_cap_text(audit_header.DBKEY, audit_header.AUDITYEAR)
    findings = get_findings(audit_header.DBKEY, audit_header.AUDITYEAR)
    captexts = xform_add_placeholder_for_missing_references(findings, captexts)
    xform_add_placeholder_for_missing_action_planned(captexts)
    xform_sanitize_for_excel(captexts)
    map_simple_columns(wb, mappings, captexts)
    wb.save(outfile)

    return wb
