import logging
import re

from .mapping_util import _open_workbook, _get_entries_by_path
from .exceptions import ExcelExtractionError
from .constants import SECTION_NAME
from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)


def _extract_generic_single_value(ir, name):
    """Extract a single value from the workbook with the defined name"""
    v = get_range_by_name(ir, name)
    return v["values"][0]


def _extract_generic_data(ir, params) -> dict:
    result: dict = {}
    try:
        _extract_generic_meta_and_field_data(ir, params, result)
        if result.get("Meta", {}).get(SECTION_NAME) == params.section:
            _extract_generic_column_data(ir, result, params)
        return result

    except AttributeError as e:
        raise ExcelExtractionError(e)


def _extract_generic_column(workbook, name):
    range = get_range_by_name(workbook, name)
    start_index = int(range["start_cell"]["row"])
    return enumerate(range["values"], start_index)


def _extract_generic_meta_and_field_data(workbook, params, result):
    for name, (target, set_fn) in params.meta_mapping.items():
        set_fn(result, target, _extract_generic_single_value(workbook, name))

    for name, (target, set_fn) in params.field_mapping.items():
        set_fn(result, target, _extract_generic_single_value(workbook, name))


def _extract_generic_column_data(workbook, result, params):
    for i, (name, (parent_target, field_target, set_fn)) in enumerate(
        params.column_mapping.items()
    ):
        for row, value in _extract_generic_column(workbook, name):
            index = (row - params.header_row) - 1  # Make it zero-indexed
            set_fn(result, f"{parent_target}[{index}].{field_target}", value)
        # Handle null entries when index/row is skipped in the first column
        if i == 0:
            entries = [
                entry if entry is not None else {}
                for entry in _get_entries_by_path(result, parent_target)
            ]
            if entries:
                set_fn(result, f"{parent_target}", entries)


# FIXME: Have an example or two of what happens
# and some unit tests around this function
def abs_ref_to_cell(ref, ndx):
    ref = ref.split(":")
    if len(ref) > ndx:
        parts = ref[ndx].split("$")
        cell = {}
        cell["column"] = parts[1]
        cell["row"] = parts[2]
        return cell
    else:
        return None


# cell obj, cell obj, worksheet name
# FIXME. Not at all clear.
# May want either unit tests and definitely documentation.
# Unit tests are tricky, they need a workbook.
def load_workbook_range(start_cell, end_cell, ws):
    values = []
    sc = f"${start_cell['column']}${start_cell['row']}"
    ec = f"${end_cell['column']}${end_cell['row']}"
    range_string = f"{sc}:{ec}"
    for cell in ws[range_string]:
        values.append(cell[0].value)
    return values


def most_common(lst):
    return max(set(lst), key=lst.count)


def appears_empty(v):
    return (v is None) or (v == 0) or (str(v).strip() == "")


def replace_range_by_name(ir, name, new_values):
    new_ir = []
    for sheet in ir:
        new_ranges = []
        for range in sheet["ranges"]:
            if range["name"] == name:
                logger.info(f"Replacing range {name}")
                range["values"] = new_values
            new_ranges.append(range)
        sheet["ranges"] = new_ranges
        new_ir.append(sheet)
    return new_ir


# FIXME: add comments
def ranges_to_rows(ranges):
    range_values = map(lambda r: r["values"], ranges)
    # Now I have a list of lists.
    list_of_rows = list(map(list, zip(*range_values)))
    list_of_rows.reverse()
    # remove trailing empties
    popping = True
    keep = []
    for row in list_of_rows:
        is_all = all(list(map(lambda v: appears_empty(v), row)))
        if is_all and popping:
            pass
        elif not is_all:
            keep.append(row)
            popping = False
        else:
            keep.append(row)
    keep.reverse()
    return keep


# FIXME: add comments
def _remove_null_rows(sheet, cutpoint):
    ranges = sheet["ranges"]
    for r in ranges:
        r["values"] = r["values"][:cutpoint]
        if "end_cell" in r and r["end_cell"]:
            c = r["end_cell"]
            # Offset by the start row minus one
            c["row"] = str(cutpoint + int(r["start_cell"]["row"]) - 1)


# FIXME: add comments
def remove_null_rows(sheet):
    ok_rows = ranges_to_rows(sheet["ranges"])
    return _remove_null_rows(sheet, len(ok_rows))


def get_sheet_by_name(sheets, name):
    for sheet in sheets:
        if sheet["name"] == name:
            return sheet


def get_range_by_name(sheets, name):
    for sheet in sheets:
        for range in sheet["ranges"]:
            if range["name"] == name:
                return range
    return None


def insert_new_range(ir, sheet_name, range_name, column, row, values):
    for sheet in ir:
        if sheet["name"] == sheet_name:
            range = {}
            range["name"] = range_name
            range["values"] = values
            range["start_cell"] = {"column": column, "row": str(row)}
            range["end_cell"] = {
                "column": column,
                "row": str(int(row) + len(values) - 1),
            }
            sheet["ranges"].append(range)
    return ir


def raise_modified_workbook(msg):
    raise ValidationError(
        (
            "Unknown",
            "",
            "Workbook",
            {"text": msg, "link": "Intake checks: no link defined"},
        )
    )


WORKBOOK_MODIFIED_ERROR = "This FAC workbook has been modified in ways we cannot process. Please download a fresh template and transfer your data."


def get_range_values_by_name(sheets, name):
    range = get_range_by_name(sheets, name)
    if range and ("values" in range):
        # logger.info("VALUES",  range["values"])
        return range["values"]
    else:
        logger.info(f"No values found for range {name}")
        # FIXME: Raise an exception?
        # Returning none to break upstream code; an exception would be better.
        raise_modified_workbook(WORKBOOK_MODIFIED_ERROR)


def remove_range_by_name(ir, name):
    new_ir = []
    for sheet in ir:
        new_ranges = []
        for range in sheet["ranges"]:
            if range["name"] == name:
                logger.info(f"Removing range {name}")
                pass
            else:
                new_ranges.append(range)
        sheet["ranges"] = new_ranges
        new_ir.append(sheet)
    return new_ir


def is_good_range_coord(s):
    if ":" in s:
        parts = s.split(":")
        if len(parts) == 2:
            return (
                True
                if (is_good_cell_coord(parts[0]) and is_good_cell_coord(parts[1]))
                else False
            )
    return False


def is_good_cell_coord(s):
    return True if re.search(r"^\$[A-Z]+\$[0-9]+$", s) else False


def is_cell_or_range_coord(s):
    return is_good_range_coord(s) or is_good_cell_coord(s)


def process_destination(dn, title, coord, sheets_by_name, workbook):
    """Process a destination for a defined name."""
    # Make sure this looks like a range string
    if is_cell_or_range_coord(coord):
        range = {}
        range["name"] = dn.name
        # If it is a range, grab both parts
        if is_good_range_coord(coord):
            range["start_cell"] = abs_ref_to_cell(coord, 0)
            range["end_cell"] = abs_ref_to_cell(coord, 1)
        # If it is a single cell (e.g. a UEI cell), then
        # make the start and end the same
        elif is_good_cell_coord(coord):
            range["start_cell"] = abs_ref_to_cell(coord, 0)
            range["end_cell"] = range["start_cell"]

        # Grab the values for this range using the start/end values
        range["values"] = load_workbook_range(
            range["start_cell"], range["end_cell"], workbook[title]
        )

        # Now, either append to a given sheet, or start a new sheet.
        if title in sheets_by_name:
            sheets_by_name[title].append(range)
        else:
            sheets_by_name[title] = [range]


def extract_workbook_as_ir(file):
    workbook = _open_workbook(file)
    sheets_by_name = {}

    for named_range_name in workbook.defined_names:
        dn = workbook.defined_names[named_range_name]
        # If the user mangles the workbook enough, we get #REF errors
        if "#ref" in dn.attr_text.lower():
            logger.info(f"Workbook has #REF errors for {named_range_name}.")
            raise_modified_workbook(WORKBOOK_MODIFIED_ERROR)
        else:
            try:
                title, coord = next(dn.destinations)
                process_destination(dn, title, coord, sheets_by_name, workbook)
            except StopIteration:
                logger.info(f"No destinations found for {named_range_name}.")
                raise_modified_workbook(WORKBOOK_MODIFIED_ERROR)

    # Build the IR, which is a list of sheets.
    sheets = []
    for name, ranges in sheets_by_name.items():
        sheet = {}
        sheet["name"] = name
        sheet["ranges"] = ranges
        sheets.append(sheet)

    # Remove all the Nones at the bottom of the sheets, since we have 10000 rows of formulas.
    for sheet in sheets:
        remove_null_rows(sheet)

    return sheets
