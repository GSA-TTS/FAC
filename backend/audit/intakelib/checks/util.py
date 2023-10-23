from .error_messages import messages
import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
)

logger = logging.getLogger(__name__)


def list_contains_non_null_values(ls):
    filtered = filter(lambda v: v is not None, ls)
    return len(list(filtered)) > 0


def get_message(key):
    if key in messages:
        return messages[key]
    else:
        return f"No error message found for <b>{key}</b>. Please contact the helpdesk."


def get_range_start_col(range):
    return range["start_cell"]["column"]


def get_range_start_row(range):
    return range["start_cell"]["row"]


def get_sheet_name_from_range_name(ir, range_name):
    for sheet in ir:
        sheet_name = sheet["name"]
        for range in sheet["ranges"]:
            if range["name"] == range_name:
                return sheet_name
    return "Uknown sheet"


# [(col1, row1, field1, link1, help-text1), (col2, row2, ...), ...]
def build_range_error_tuple(ir, range, range_name, text):
    return (
        get_range_start_col(range),
        get_range_start_row(range),
        get_sheet_name_from_range_name(ir, range_name),
        {"text": text, "link": "Intake checks: no link defined"},
    )


def build_cell_error_tuple(ir, range, ndx, message):
    return (
        get_range_start_col(range),
        int(get_range_start_row(range)) + ndx,
        get_sheet_name_from_range_name(ir, range["name"]),
        {"text": message, "link": "Intake checks: no link defined"},
    )


def get_missing_value_errors(ir, range_name, message_key):
    range_data = get_range_by_name(ir, range_name)
    errors = []
    if range_data:
        for index, value in enumerate(range_data["values"]):
            if (value is None) or (str(value).strip() == ""):
                errors.append(
                    build_cell_error_tuple(
                        ir,
                        range_data,
                        index,
                        get_message(message_key),
                    )
                )

    return errors


def get_names_of_all_ranges(data):
    names = []
    for entry in data:
        if "ranges" in entry:
            for range_item in entry["ranges"]:
                if "name" in range_item:
                    names.append(range_item["name"])
    return names
