from ..transforms.xform_string_to_bool import (
    string_to_bool,
)
from ..transforms.xform_string_to_string import (
    string_to_string,
)
from ..transforms.xform_string_to_int import string_to_int
from ..exception_utils import (
    DataMigrationError,
    DataMigrationValueError,
)
from ..workbooklib.templates import sections_to_template_paths
from ..models import (
    ELECAUDITS as Audits,
    ELECAUDITHEADER as AuditHeader,
)

from openpyxl.utils.cell import (
    rows_from_range,
    coordinate_from_string,
    column_index_from_string,
)

import logging


logger = logging.getLogger(__name__)


def set_range(wb, range_name, values, default=None, conversion_fun=str):
    """
    Helper to set a range of values. Takes a named range, and then walks down
    the range, filling in the given values.

    wb (Workbook)       The workbook
    range_name (string) Name of the range to set
    values (iterable)   Values to set within the range
    default (any)       Default value to use; defaults to None.
    conversion (func)   Conversion function to apply to individual values; defaults to str().
    """
    the_range = wb.defined_names[range_name]
    dests = the_range.destinations

    sheet_title, coord = None, None
    for cur_sheet_title, cur_coord in dests:
        if sheet_title or coord:
            # `destinations` is meant to be iterated over, but we only expect one value
            raise DataMigrationValueError(
                f"{range_name} has more than one destination",
                "multiple_destinations",
            )
        else:
            sheet_title, coord = cur_sheet_title, cur_coord

    ws = None
    try:
        ws = wb[sheet_title]
    except KeyError:
        raise KeyError(f"Sheet title '{sheet_title}' not found in workbook")

    values = list(values)
    for i, row in enumerate(rows_from_range(coord)):
        # Iterate over the rows, but stop when we run out of values
        value = None
        try:
            value = values[i]
        except IndexError:
            break

        # Get the row and column to set the current value
        cell = row[0]  # [('B12',)] -> ('B12',)
        col_str, row = coordinate_from_string(cell)  # ('B12',) -> 'B', 12
        col = column_index_from_string(col_str)  # 'B' -> 2

        # Check for the type and apply the correct conversion method
        converted_value = apply_conversion_function(value, default, conversion_fun)
        # Set the value of the cell
        ws.cell(row=row, column=col, value=converted_value)


def apply_conversion_function(value, default, conversion_function):
    """
    Helper to apply a conversion function to a value, or use a default value
    """
    if value is None and default is None:
        raise DataMigrationValueError(
            "No value or default provided",
            "no_value_or_default",
        )

    selected_value = value if value is not None else default

    if conversion_function is str:
        new_value = string_to_string(selected_value)
    elif conversion_function is int:
        new_value = string_to_int(selected_value)
    elif conversion_function is bool:
        new_value = string_to_bool(selected_value)
    else:
        new_value = conversion_function(selected_value)

    return new_value


def set_workbook_uei(workbook, uei):
    """Sets the UEI value in the workbook's designated UEI cell"""
    if not uei:
        raise DataMigrationError(
            "UEI value is missing or invalid.",
            "invalid_uei",
        )
    set_range(workbook, "auditee_uei", [uei])


def get_audit_header(dbkey, year):
    """Returns the AuditHeader record for the given dbkey and audit year."""
    try:
        audit_header = AuditHeader.objects.get(DBKEY=dbkey, AUDITYEAR=year)
    except AuditHeader.DoesNotExist:
        raise DataMigrationError(
            f"No audit header record found for dbkey: {dbkey} and audit year: {year}",
            "missing_audit_header",
        )
    return audit_header


def map_simple_columns(wb, mappings, values):
    len_passed_in = len(mappings)
    unique_fields = set()
    for mapping in mappings:
        unique_fields.add(mapping.in_sheet)
    if len_passed_in != len(unique_fields):
        logger.info(f"unique: {len(unique_fields)} list: {len(mappings)}")
        logger.error(
            "You repeated a field in the mappings: {}".format(
                list(map(lambda m: m.in_sheet, mappings))
            )
        )
        raise DataMigrationError(
            "Invalid mappings. You repeated a field in the mappings",
            "invalid_mappings",
        )

    # Map all the simple ones
    for m in mappings:
        set_range(
            wb,
            m.in_sheet,
            map(lambda v: getattr(v, m.in_db), values),
            m.default,
            m.type,
        )


def get_template_name_for_section(section):
    """
    Return a workbook template name corresponding to the given section
    """
    if section in sections_to_template_paths:
        template_name = sections_to_template_paths[section].name
        return template_name
    else:
        raise DataMigrationValueError(
            f"Unknown section {section}",
            "invalid_section",
        )


def get_audits(dbkey, year):
    """Returns Audits records for the given dbkey and audit year."""
    results = Audits.objects.filter(DBKEY=dbkey, AUDITYEAR=year)
    return sort_by_field(results, "CFDASEQNUM")


def xform_sanitize_for_excel(texts):
    """Sanitize finding text for excel when necessary."""
    for text in texts:
        if text.TEXT and contains_illegal_characters(text.TEXT):
            sanitized_value = sanitize_for_excel(text.TEXT)
            text.TEXT = sanitized_value


def contains_illegal_characters(value):
    """Check if a string contains illegal characters."""
    for char in value:
        # Control characters have ordinals less than 32
        # space character has an ordinal of 32
        if ord(char) < 32 and char not in "\n\r\t":
            return True
    return False


def sanitize_for_excel(value):
    """Remove illegal characters from a string."""
    # Remove all control characters except newline and tab
    sanitized_value = "".join(
        char for char in value if ord(char) >= 32 or char in "\n\r\t"
    )
    return sanitized_value


def sort_by_field(records, sort_field):
    """
    Sorts records by a specified field. The values of the field are converted to integers before sorting.
    """
    return sorted(records, key=lambda record: int(getattr(record, sort_field)))
