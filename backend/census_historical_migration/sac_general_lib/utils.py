from datetime import date


def _create_json_from_db_object(gobj, mappings):
    json_obj = {}
    for mapping in mappings:
        if mapping.in_db is not None:
            value = getattr(gobj, mapping.in_db, mapping.default)
        else:
            value = mapping.default
        # Fields with a value of None are skipped to maintain consistency with the logic
        # used in workbook data extraction and to prevent converting None into the string "None".
        if value is not None:
            json_obj[mapping.in_form] = value
    return json_obj


def _boolean_field(json_obj, field_name):
    json_obj[field_name] = json_obj.get(field_name, "N") == "Y"
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
    year, month_abbr, day = parts
    month = lookup[month_abbr]
    return date(int(year) + 2000, month, int(day))
