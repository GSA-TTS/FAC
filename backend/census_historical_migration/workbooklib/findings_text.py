from django.conf import settings

from ..transforms.xform_string_to_string import (
    string_to_string,
)
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
from ..models import ELECFINDINGSTEXT as FindingsText
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
    SheetFieldMap("text_of_finding", "TEXT", "finding_text", None, str),
    SheetFieldMap(
        "contains_chart_or_table",
        "CHARTSTABLES",
        WorkbookFieldInDissem,
        None,
        uppercase_y_or_n,
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


def xform_add_placeholder_for_missing_text_of_finding(findings_texts):
    """
    Add placeholder text for missing findings_text.
    """
    for findings_text in findings_texts:
        if string_to_string(findings_text.FINDINGREFNUMS) and not string_to_string(
            findings_text.TEXT
        ):
            findings_text.TEXT = settings.GSA_MIGRATION


def track_invalid_records_with_more_findings_texts_than_findings(
    findings, findings_texts
):
    """If there are more findings_texts than findings,
    track all the records as invalid records."""

    finding_refnums = get_reference_numbers_from_findings(findings)
    findings_text_refnums = get_reference_numbers_from_text_records(findings_texts)
    invalid_records = []
    extra_findings_texts = findings_text_refnums.difference(finding_refnums)
    if len(extra_findings_texts) > 0:
        invalid_records = []
        for findings_text_refnum in findings_text_refnums:
            census_data_tuples = [
                ("FINDINGREFNUMS", findings_text_refnum),
            ]
            track_invalid_records(
                census_data_tuples,
                "finding_ref_number",
                findings_text_refnum,
                invalid_records,
            )

    if invalid_records:
        InvalidRecord.append_invalid_finding_text_records(invalid_records)
        InvalidRecord.append_validations_to_skip("check_ref_number_in_findings_text")
        InvalidRecord.append_invalid_migration_tag(
            INVALID_MIGRATION_TAGS.EXTRA_FINDING_REFERENCE_NUMBERS_IN_FINDINGSTEXT
        )


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

    track_invalid_records_with_more_findings_texts_than_findings(
        findings, findings_texts
    )
    findings_texts = xform_add_placeholder_for_missing_references(
        findings, findings_texts
    )
    xform_add_placeholder_for_missing_text_of_finding(findings_texts)
    xform_sanitize_for_excel(findings_texts)
    map_simple_columns(wb, mappings, findings_texts)

    wb.save(outfile)

    return wb
