from django.conf import settings
from .error_messages import messages
import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
)
from django.core.exceptions import ValidationError

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


def appears_empty(v):
    return (v is None) or (str(v).strip() == "")


def is_value_marked_na(v):
    value = str(v).strip()
    return value == "N/A"


def is_yes_or_no_or_gsa_migration(v):
    """Returns true if the value is Y, N, or GSA_MIGRATION."""
    # `GSA_MIGRATION` was added here to allow `contains_chart_or_table`
    # in historic data migration to pass validation.
    value = str(v).strip()

    return value == "Y" or value == "N" or value == settings.GSA_MIGRATION


def get_missing_value_errors(ir, range_name, message_key):
    range_data = get_range_by_name(ir, range_name)
    errors = []
    if range_data:
        for index, value in enumerate(range_data["values"]):
            if appears_empty(value):
                errors.append(
                    build_cell_error_tuple(
                        ir,
                        range_data,
                        index,
                        get_message(message_key),
                    )
                )

    return errors


def invalid_y_or_n_entry(ir, range_name, message_key):
    range_data = get_range_by_name(ir, range_name)
    errors = []
    if range_data:
        for index, value in enumerate(range_data["values"]):
            if not is_yes_or_no_or_gsa_migration(value):
                errors.append(
                    build_cell_error_tuple(
                        ir,
                        range_data,
                        index,
                        get_message(message_key).format(value),
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


def safe_int_conversion(ir, range_name, other_values_allowed=None):
    range_data = get_range_by_name(ir, range_name)
    errors = []
    new_values = []
    if range_data:
        for index, value in enumerate(range_data["values"]):
            try:
                float_value = float(value)
                if float_value.is_integer():
                    new_values.append(int(float_value))
                else:
                    raise ValueError
            except (ValueError, TypeError):
                # If the value is None, we keep it. This is because some int fields are optional.
                # For non optional fields, there is a check for missing required fields that will raise an error.
                if (value is None) or (
                    other_values_allowed and value in other_values_allowed
                ):
                    new_values.append(value)
                else:
                    errors.append(
                        build_cell_error_tuple(
                            ir,
                            range_data,
                            index,
                            get_message("check_integer_values").format(value),
                        )
                    )
        if len(errors) > 0:
            logger.info("Raising a validation error.")
            raise ValidationError(errors)
    new_ir = replace_range_by_name(ir, range_name, new_values)
    return new_ir
