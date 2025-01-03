import logging
from datetime import datetime, timezone
import sys

from census_historical_migration.report_type_flag import AceFlag

from ..transforms.xform_string_to_string import (
    string_to_string,
)
from ..transforms.xform_string_to_int import string_to_int
from ..transforms.xform_string_to_bool import string_to_bool
from ..exception_utils import DataMigrationValueError

logger = logging.getLogger(__name__)


def create_json_from_db_object(gobj, mappings):
    """Constructs a JSON object from a database object using a list of mappings."""
    json_obj = {}
    for mapping in mappings:
        if mapping.in_db:
            value = getattr(gobj, mapping.in_db, mapping.default)
        else:
            value = mapping.default
        # Fields with a value of None are skipped to maintain consistency with the logic
        # used in workbook data extraction and to prevent converting None into the string "None".
        if value is None or (value == "" and AceFlag.get_ace_report_flag()):
            continue
        # Check for the type and apply the correct conversion method
        if mapping.type is str:
            value = string_to_string(value)
        elif mapping.type is bool:
            value = string_to_bool(value)
        elif mapping.type is int:
            value = string_to_int(value)
        else:
            value = mapping.type(value)
        json_obj[mapping.in_form] = value

    return json_obj


def xform_census_date_to_datetime(date_string):
    """Convert a census date string from '%m/%d/%Y %H:%M:%S' format to 'YYYY-MM-DD' format."""
    # Parse the string into a datetime object
    formats = ["%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_string, fmt)
            return dt.date()
        except ValueError:
            continue
    # Raise a custom exception or a ValueError with a descriptive message
    raise DataMigrationValueError(
        f"Date string '{date_string}' is not in the expected formats: '%m/%d/%Y %H:%M:%S' or 'YYYY-MM-DD HH:MM:SS'",
        "invalid_date",
    )


def xform_census_date_to_utc_time(date_string):
    """Convert a date string from '%m/%d/%Y %H:%M:%S' format to 'YYYY-MM-DD HH:MM:SS.ffffff±HH' format."""
    formats = ["%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S"]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_string, fmt)
            dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue

    raise DataMigrationValueError(
        f"Date string '{date_string}' is not in the expected formats: '%m/%d/%Y %H:%M:%S' or 'YYYY-MM-DD HH:MM:SS'",
        "invalid_date",
    )

    return dt


def normalize_year_string_or_exit(year_string):
    """
    Normalizes a year string to a four-digit year format or exits the program if the year string is invalid.
    """
    # Do not use this function elsewhere to normilize year strings
    # or it will quit the program if the year is invalid.
    # The goal here is to quickly fail django commands if the year is invalid.
    try:
        year = int(year_string)
    except ValueError:
        logger.error("Invalid year string.")
        sys.exit(-1)

    if 16 <= year < 23:
        return str(year + 2000)
    elif 2016 <= year < 2023:
        return year_string
    else:
        logger.error("Invalid year string. Audit year must be between 2016 and 2022")
        sys.exit(-1)


def is_single_word(s):
    """Returns True if the string is a single word, False otherwise."""
    return len(s.split()) == 1
