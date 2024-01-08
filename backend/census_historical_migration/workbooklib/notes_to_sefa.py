import inspect
from django.conf import settings

from ..change_record import CensusRecord, ChangeRecord, GsaFacRecord
from ..api_test_helpers import generate_dissemination_test_table
from ..transforms.xform_retrieve_uei import xform_retrieve_uei
from ..exception_utils import DataMigrationError
from ..transforms.xform_string_to_string import string_to_string
from ..models import ELECNOTES as Notes
from ..workbooklib.excel_creation_utils import (
    set_range,
    map_simple_columns,
    set_workbook_uei,
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


def track_data_transformation(original_value, changed_value, transformation_function):
    """Tracks transformation for minimis rate."""
    census_data = [
        CensusRecord("CONTENT", original_value).to_dict(),
    ]
    gsa_fac_data = GsaFacRecord("is_minimis_rate_used", changed_value).to_dict()

    ChangeRecord.extend_note_changes(
        [
            {
                "census_data": census_data,
                "gsa_fac_data": gsa_fac_data,
                "transformation_function": [transformation_function],
            }
        ]
    )


def xform_is_minimis_rate_used(rate_content):
    """Determines if the de minimis rate was used based on the given text."""

    # Transformation recorded.

    # Patterns that indicate the de minimis rate was NOT used
    not_used_patterns = [
        r"not\s+to\s+use",
        r"not\s+opt\s+to\s+use",
        r"not\s+us(e|ed)",
        r"not\s+elec(t|ted)",
        r"has\s+not\s+charged.*not\s+applicable",
        r"did\s+not\s+charge\s+indirect\s+costs",
    ]

    # Patterns that indicate the de minimis rate WAS used
    used_patterns = [r"used", r"elected\s+to\s+use", r"uses.*allowed"]

    function_name = inspect.currentframe().f_code.co_name
    # Check for each pattern in the respective lists
    for pattern in not_used_patterns:
        if re.search(pattern, rate_content, re.IGNORECASE):
            track_data_transformation(rate_content, "N", function_name)
            return "N"
    for pattern in used_patterns:
        if re.search(pattern, rate_content, re.IGNORECASE):
            track_data_transformation(rate_content, "Y", function_name)
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
    except Notes.DoesNotExist:
        logger.info(f"De Minimis cost rate not found for dbkey: {dbkey}")
        rate = ""
    return rate


def _get_notes(dbkey, year):
    """Get the notes for a given dbkey and audit year."""
    # https://facdissem.census.gov/Documents/DataDownloadKey.xlsx
    # The TYPEID column determines which field in the form a given row corresponds to.
    # TYPEID=3 is for notes, which have sequence numbers... that must align somewhere.
    return Notes.objects.filter(DBKEY=dbkey, AUDITYEAR=year, TYPE_ID="3").order_by(
        "SEQ_NUMBER"
    )


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
    rate_content = _get_minimis_cost_rate(audit_header.DBKEY, audit_header.AUDITYEAR)
    policies_content = _get_accounting_policies(
        audit_header.DBKEY, audit_header.AUDITYEAR
    )
    is_minimis_rate_used = xform_is_minimis_rate_used(rate_content)

    set_range(wb, "accounting_policies", [policies_content])
    set_range(wb, "is_minimis_rate_used", [is_minimis_rate_used])
    set_range(wb, "rate_explained", [rate_content])

    contains_chart_or_tables = [settings.GSA_MIGRATION] * len(notes)

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

    table = generate_dissemination_test_table(
        audit_header, "notes_to_sefa", mappings, notes
    )
    table["singletons"] = dict()
    table["singletons"]["accounting_policies"] = policies_content
    table["singletons"]["is_minimis_rate_used"] = is_minimis_rate_used
    table["singletons"]["rate_explained"] = rate_content
    table["singletons"]["auditee_uei"] = uei

    if notes:
        for obj, ar in zip(table["rows"], contains_chart_or_tables):
            obj["fields"].append("contains_chart_or_table")
            obj["values"].append(ar)

    return (wb, table)
