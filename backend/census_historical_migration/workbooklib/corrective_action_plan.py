from django.conf import settings

from ..transforms.xform_string_to_string import string_to_string

from ..workbooklib.findings import get_findings
from ..transforms.xform_retrieve_uei import xform_retrieve_uei
from ..transforms.xform_uppercase_y_or_n import uppercase_y_or_n
from ..workbooklib.excel_creation_utils import (
    get_reference_numbers_from_findings,
    get_reference_numbers_from_text_records,
    map_simple_columns,
    set_workbook_uei,
    sort_by_field,
    xform_sanitize_for_excel,
    track_invalid_records,
)
from ..base_field_maps import (
    SheetFieldMap,
    WorkbookFieldInDissem,
)
from ..workbooklib.templates import sections_to_template_paths
from ..models import ELECCAPTEXT as CapText
from audit.fixtures.excel import FORM_SECTIONS
from ..invalid_migration_tags import INVALID_MIGRATION_TAGS
from ..invalid_record import InvalidRecord

import openpyxl as pyxl

import logging

logger = logging.getLogger(__name__)

mappings = [
    SheetFieldMap(
        "reference_number", "FINDINGREFNUMS", "finding_ref_number", None, str
    ),
    SheetFieldMap("planned_action", "TEXT", WorkbookFieldInDissem, None, str),
    SheetFieldMap(
        "contains_chart_or_table",
        "CHARTSTABLES",
        WorkbookFieldInDissem,
        None,
        uppercase_y_or_n,
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


def xform_add_placeholder_for_missing_action_planned_text(captexts):
    """
    Add placeholder for missing action planned texts.
    """
    for captext in captexts:
        if string_to_string(captext.FINDINGREFNUMS) and not string_to_string(
            captext.TEXT
        ):
            captext.TEXT = settings.GSA_MIGRATION


def track_invalid_records_with_more_captexts_less_findings(findings, captexts):
    """If there are more captexts than findings,
    track the records as invalid records."""

    finding_refnums = get_reference_numbers_from_findings(findings)
    captext_refnums = get_reference_numbers_from_text_records(captexts)
    invalid_records = []
    if len(captext_refnums.difference(finding_refnums)) > 0:
        invalid_records = []
        for captext_refnum in captext_refnums:
            census_data_tuples = [
                ("FINDINGREFNUMS", captext_refnum),
            ]
            track_invalid_records(
                census_data_tuples,
                "finding_ref_number",
                captext_refnum,
                invalid_records,
            )

    if invalid_records:
        InvalidRecord.append_invalid_cap_text_records(invalid_records)
        InvalidRecord.append_validations_to_skip("check_ref_number_in_cap")
        InvalidRecord.append_invalid_migration_tag(
            INVALID_MIGRATION_TAGS.EXTRA_FINDING_REFERENCE_NUMBERS_IN_CAPTEXT
        )
    return invalid_records


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

    invalid_record = track_invalid_records_with_more_captexts_less_findings(
        findings, captexts
    )
    if not invalid_record:
        captexts = xform_add_placeholder_for_missing_references(findings, captexts)

    xform_add_placeholder_for_missing_action_planned_text(captexts)
    xform_sanitize_for_excel(captexts)
    map_simple_columns(wb, mappings, captexts)

    wb.save(outfile)

    return wb
