from django.conf import settings

from ..change_record import CensusRecord, InspectionRecord, GsaFacRecord
from ..transforms.xform_retrieve_uei import xform_retrieve_uei
from ..exception_utils import DataMigrationError
from ..transforms.xform_string_to_string import string_to_string
from ..models import ELECNOTES as Notes
from ..workbooklib.excel_creation_utils import (
    set_range,
    map_simple_columns,
    set_workbook_uei,
    sort_by_field,
)
from ..base_field_maps import SheetFieldMap
from ..workbooklib.templates import sections_to_template_paths
from audit.fixtures.excel import FORM_SECTIONS

import openpyxl as pyxl

import re
import logging


logger = logging.getLogger(__name__)

mappings = [
    SheetFieldMap("note_title", "TITLE", "title", None, str),
    SheetFieldMap("note_content", "CONTENT", "content", None, str),
]


def xform_cleanup_string(s):
    """Transforms a string to a string, cleaning up unicode characters."""
    value = string_to_string(s)
    if value:
        # FIXME-MSHD: This is a transformation that we may want to record
        return str(value.encode("utf-8").decode("ascii", "ignore"))
    return ""


def track_data_transformation(
    original_value,
    changed_value,
    transformation_functions,
    gsa_field="is_minimis_rate_used",
):
    """Tracks transformation for minimis rate."""
    census_data = [
        CensusRecord("CONTENT", original_value).to_dict(),
    ]
    gsa_fac_data = GsaFacRecord(gsa_field, changed_value).to_dict()

    InspectionRecord.append_note_changes(
        [
            {
                "census_data": census_data,
                "gsa_fac_data": gsa_fac_data,
                "transformation_functions": [transformation_functions],
            }
        ]
    )


def xform_is_minimis_rate_used(rate_content, index=""):
    """Determines if the de minimis rate was used based on the given text."""

    # Transformation recorded.

    # Patterns that indicate the de minimis rate was NOT used
    not_used_patterns = [
        r"not\s+to\s+use",
        r"not\s+opt\s+to\s+use",
        r"not\s+us(e|ed)",
        r"not\s+elec(t|ted)",
        r"not\s+applicable",
        r"not\s+(to\s+)?utilize",
        r"has\s+elected\s+not",
        r"no\s+election",
        r"not\s+(made|make)\s+(this|an)\s+election",
        r"did\s+not\s+charge\s+indirect\s+costs",
        r"not\s+eligible\s+to\s+use",
        r"rather\s+than\s+the\s+10%",
        r"no\s+additional\s+indirect\s+costs",
        r"(rate|costs)\s+does\s+not\s+apply",
        r"not\s+based\s+on\s+eligible\s+costs",
        r"no\s+indirect\s+costs?",
    ]

    # Patterns that indicate the de minimis rate WAS used
    used_patterns = [
        r"used",
        r"elected\s+to\s+use",
        r"uses.*allowed",
        r"has\s+adopted",
        r"elected\s+to",
        r"is\s+subject\s+to\s+the\s+10-percent",
        r"utilize(d|s)?\s+(a|an|the)\s+(10|ten)",
    ]

    if index == "1":
        track_data_transformation(rate_content, "Y", "xform_is_minimis_rate_used")
        return "Y"
    elif index == "2":
        track_data_transformation(rate_content, "N", "xform_is_minimis_rate_used")
        return "N"
    elif index == "3":
        track_data_transformation(rate_content, "Both", "xform_is_minimis_rate_used")
        return "Both"
    if not rate_content:
        track_data_transformation(
            rate_content, settings.GSA_MIGRATION, "xform_is_minimis_rate_used"
        )
        return settings.GSA_MIGRATION
    # Check for each pattern in the respective lists
    for pattern in not_used_patterns:
        if re.search(pattern, rate_content, re.IGNORECASE):
            track_data_transformation(rate_content, "N", "xform_is_minimis_rate_used")
            return "N"
    for pattern in used_patterns:
        if re.search(pattern, rate_content, re.IGNORECASE):
            track_data_transformation(rate_content, "Y", "xform_is_minimis_rate_used")
            return "Y"

    raise DataMigrationError(
        "Unable to determine if the de minimis rate was used.",
        "unexpected_minimis_rate_text",
    )


def _get_accounting_policies(dbkey, year):
    # https://facdissem.census.gov/Documents/DataDownloadKey.xlsx
    # The TYPEID column determines which field in the form a given row corresponds to.
    # TYPEID=1 is the description of significant accounting policies.
    """Get the accounting policies for a given dbkey and audit year."""

    try:
        note = Notes.objects.get(DBKEY=dbkey, AUDITYEAR=year, TYPE_ID="1")
        content = string_to_string(note.CONTENT)
    except Notes.DoesNotExist:
        logger.info(f"No accounting policies found for dbkey: {dbkey}")
        content = ""

    return content


def _get_minimis_cost_rate(dbkey, year):
    """Get the De Minimis cost rate for a given dbkey and audit year."""
    # https://facdissem.census.gov/Documents/DataDownloadKey.xlsx
    # The TYPEID column determines which field in the form a given row corresponds to.
    # TYPEID=2 is the De Minimis cost rate.

    try:
        note = Notes.objects.get(DBKEY=dbkey, AUDITYEAR=year, TYPE_ID="2")
        rate = string_to_string(note.CONTENT)
        index = string_to_string(note.NOTE_INDEX)
    except Notes.DoesNotExist:
        logger.info(f"De Minimis cost rate not found for dbkey: {dbkey}")
        rate = ""
        index = ""
    return rate, index


def _get_notes(dbkey, year):
    """Get the notes for a given dbkey and audit year."""
    # https://facdissem.census.gov/Documents/DataDownloadKey.xlsx
    # The TYPEID column determines which field in the form a given row corresponds to.
    # TYPEID=3 is for notes, which have sequence numbers... that must align somewhere.
    results = Notes.objects.filter(DBKEY=dbkey, AUDITYEAR=year, TYPE_ID="3")

    return sort_by_field(results, "SEQ_NUMBER")


def xform_missing_notes_records_v2(audit_header, policies_content, rate_content):
    """Transforms missing notes records for 2022, 2021, 2020, 2019, 2016, 2017 and 2018 audits.
    Note:
    This function replaces xform_missing_notes_records function.
    This function covers all years 2016 through 2022.
    This function tracks census data for policies_content and rate_content."""

    if string_to_string(audit_header.AUDITYEAR) in [
        "2022",
        "2021",
        "2020",
        "2019",
        "2018",
        "2017",
        "2016",
    ] and not (policies_content or rate_content):
        track_data_transformation(
            policies_content,
            settings.GSA_MIGRATION,
            "xform_missing_notes_records_v2",
            "accounting_policies",
        )
        policies_content = settings.GSA_MIGRATION
        track_data_transformation(
            rate_content,
            settings.GSA_MIGRATION,
            "xform_missing_notes_records_v2",
            "rate_explained",
        )
        rate_content = settings.GSA_MIGRATION
    return policies_content, rate_content


def xform_missing_note_title_and_content(notes):
    """Transforms missing note title and note content."""
    for note in notes:
        if string_to_string(note.TITLE) == "" and string_to_string(note.CONTENT) != "":
            track_data_transformation(
                note.TITLE,
                settings.GSA_MIGRATION,
                "xform_missing_note_title_and_content",
                "note_title",
            )
            note.TITLE = settings.GSA_MIGRATION

        if string_to_string(note.CONTENT) == "" and string_to_string(note.TITLE) != "":
            track_data_transformation(
                note.CONTENT,
                settings.GSA_MIGRATION,
                "xform_missing_note_title_and_content",
                "content",
            )
            note.CONTENT = settings.GSA_MIGRATION

    return notes


def xform_rate_content(rate_content):
    """Transform empty rate_content"""

    if rate_content == "":
        track_data_transformation(
            rate_content,
            settings.GSA_MIGRATION,
            "xform_rate_content",
            "content",
        )
        rate_content = settings.GSA_MIGRATION
    return rate_content


def xform_policies_content(policies_content):
    """Transform empty policies_content"""

    if policies_content == "":
        track_data_transformation(
            policies_content,
            settings.GSA_MIGRATION,
            "xform_policies_content",
            "content",
        )
        policies_content = settings.GSA_MIGRATION

    return policies_content


def xform_sanitize_policies_content(policies_content):
    """Transformation to Remove leading special characters in policies_content"""

    xformed_policies_content = policies_content.lstrip("=")
    if xformed_policies_content != policies_content:
        track_data_transformation(
            policies_content,
            xformed_policies_content,
            "xform_sanitize_policies_content",
            "content",
        )
        policies_content = xformed_policies_content

    return policies_content


def generate_notes_to_sefa(audit_header, outfile):
    """
    Generates notes to SEFA workbook for a given audit header.
    """
    logger.info(
        f"--- generate notes to sefa {audit_header.DBKEY} {audit_header.AUDITYEAR}---"
    )

    wb = pyxl.load_workbook(sections_to_template_paths[FORM_SECTIONS.NOTES_TO_SEFA])
    uei = xform_retrieve_uei(audit_header.UEI)
    set_workbook_uei(wb, uei)
    notes = _get_notes(audit_header.DBKEY, audit_header.AUDITYEAR)
    notes = xform_missing_note_title_and_content(notes)
    rate_content, index = _get_minimis_cost_rate(
        audit_header.DBKEY, audit_header.AUDITYEAR
    )
    policies_content = _get_accounting_policies(
        audit_header.DBKEY, audit_header.AUDITYEAR
    )
    is_minimis_rate_used = xform_is_minimis_rate_used(rate_content, index)
    policies_content, rate_content = xform_missing_notes_records_v2(
        audit_header, policies_content, rate_content
    )

    rate_content = xform_rate_content(rate_content)
    policies_content = xform_policies_content(policies_content)
    policies_content = xform_sanitize_policies_content(policies_content)

    set_range(wb, "accounting_policies", [policies_content])
    set_range(wb, "is_minimis_rate_used", [is_minimis_rate_used])
    set_range(wb, "rate_explained", [rate_content])

    contains_chart_or_tables = []
    for note in notes:
        if string_to_string(note.TITLE) == "" and string_to_string(note.CONTENT) == "":
            contains_chart_or_tables.append("")
        else:
            contains_chart_or_tables.append(settings.GSA_MIGRATION)

    # Map the rest as notes.
    map_simple_columns(wb, mappings, notes)

    set_range(
        wb,
        "contains_chart_or_table",
        contains_chart_or_tables,
        "N",
        str,
    )
    wb.save(outfile)

    return wb
