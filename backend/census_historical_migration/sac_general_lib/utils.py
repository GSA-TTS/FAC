from datetime import date, datetime
from census_historical_migration.transforms.xform_string_to_date import string_to_date
from census_historical_migration.transforms.xform_string_to_string import (
    string_to_string,
)
from census_historical_migration.transforms.xform_string_to_int import string_to_int
from census_historical_migration.transforms.xform_string_to_bool import string_to_bool


def _create_json_from_db_object(gobj, mappings):
    json_obj = {}
    for mapping in mappings:
        if mapping.in_db is not None:
            value = getattr(gobj, mapping.in_db, mapping.default)
        else:
            value = mapping.default
        # Fields with a value of None are skipped to maintain consistency with the logic
        # used in workbook data extraction and to prevent converting None into the string "None".
        if value is None:
            continue
        # Check for the type and apply the correct conversion method
        if mapping.type is str:
            value = string_to_string(value)
        elif mapping.type is bool:
            value = string_to_bool(value)
        elif mapping.type is int:
            value = string_to_int(value)
        elif mapping.type is date:
            value = string_to_date(value)

        json_obj[mapping.in_form] = value
    return json_obj


def _census_date_to_datetime(cd):
    lookup = {
        "JAN": 1,
        "FEB": 2,
        "MAR": 3,
        "APR": 4,
        "MAY": 5,
        "JUN": 6,
        "JUL": 7,
        "AUG": 8,
        "SEP": 9,
        "OCT": 10,
        "NOV": 11,
        "DEC": 12,
    }
    parts = cd.split("-")
    if len(parts) != 3 or parts[1] not in lookup:
        raise ValueError("Invalid date format or month abbreviation in census date")
    day, month_abbr, year = parts
    month = lookup[month_abbr]

    return date(int(year) + 2000, month, int(day))


def xform_census_date_to_datetime(date_string):
    """Convert a census date string from '%m/%d/%Y %H:%M:%S' format to 'YYYY-MM-DD' format."""
    # Parse the string into a datetime object
    dt = datetime.strptime(date_string, "%m/%d/%Y %H:%M:%S")
    # Extract and return the date part
    return dt.date()
