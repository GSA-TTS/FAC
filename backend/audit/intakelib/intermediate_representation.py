import pprint

from .mapping_util import _open_workbook, _get_entries_by_path
from .exceptions import ExcelExtractionError
from .constants import SECTION_NAME
import time


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


# Better to work from the end, and
# find the first row that is not None/0.
def find_last_none(ls):
    rev = list(reversed(ls))
    ndx = len(rev)
    for o in rev:
        if (isinstance(o, int) and (o != 0)) or isinstance(o, str) and (o != ""):
            return ndx
        else:
            ndx -= 1
    # Exception
    return 1


def remove_null_rows(sheet):
    ranges = sheet["ranges"]
    values = map(lambda r: r["values"], ranges)
    null_locations = []
    for ls in values:
        null_locations.append(find_last_none(ls))
    cutpoint = max(null_locations)
    print(f"CUTPOINT")
    for r in ranges:
        r["values"] = r["values"][:cutpoint]
        if "end_cell" in r and r["end_cell"]:
            c = r["end_cell"]
            # Offset by the start row minus one
            c["row"] = str(cutpoint + int(r["start_cell"]["row"]) - 1)


def get_sheet_by_name(sheets, name):
    for sheet in sheets:
        print("SHEET", name)
        if sheet["name"] == name:
            return sheet


def get_range_by_name(sheets, name):
    for sheet in sheets:
        for range in sheet["ranges"]:
            if range["name"] == name:
                return range
    return None


def extract_workbook_as_ir(file):
    workbook = _open_workbook(file)
    by_name = {}
    for named_range_name in workbook.defined_names:
        dn = workbook.defined_names[named_range_name]
        title, coord = next(dn.destinations)
        range = {}
        range["name"] = dn.name
        range["start_cell"] = abs_ref_to_cell(coord, 0)
        range["end_cell"] = abs_ref_to_cell(coord, 1)
        if not range["end_cell"]:
            coord = f"{coord}:{coord}"
            range["end_cell"] = range["start_cell"]
        range["values"] = load_workbook_range(
            range["start_cell"], range["end_cell"], workbook[title]
        )
        if title in by_name:
            by_name[title].append(range)
        else:
            by_name[title] = [range]

    sheets = []
    for name, ranges in by_name.items():
        sheet = {}
        sheet["name"] = name
        sheet["ranges"] = ranges
        sheets.append(sheet)

    for sheet in sheets:
        remove_null_rows(sheet)

    return sheets
