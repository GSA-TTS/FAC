from .error_messages import messages
import logging

logger = logging.getLogger(__name__)

def list_contains_non_null_values(ls):
    filtered = filter(lambda v: v is not None, ls)
    return len(list(filtered)) > 0

def get_message(key):
    if key in messages:
        return messages[key]
    else:
        return f'No error message found for "{key}". Please contact the helpdesk.'

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
        { 
            "text": text,
            "link": "Intake checks: no link defined"
        }
    )


def build_cell_error_tuple(ir, range, ndx, message):
    return (
        get_range_start_col(range),
        int(get_range_start_row(range)) + ndx,
        get_sheet_name_from_range_name(ir, range["name"]),
        { 
            "text": message,
            "link": "Intake checks: no link defined"
        }
    )
