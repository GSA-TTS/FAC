from collections import namedtuple
import pydash
import re
from typing import Any, Callable
import logging
from typing import Any, Callable
from openpyxl import load_workbook, Workbook
from openpyxl.cell import Cell
from audit.fixtures.excel import (
    UNKNOWN_WORKBOOK,
)

from .constants import (
    SECTION_NAME,
    AWARD_ENTITY_NAME_PATH,
    AWARD_ENTITY_NAME_KEY,
    AWARD_ENTITY_ID_PATH,
    AWARD_ENTITY_ID_KEY
    )

from .exceptions import ExcelExtractionError

logger = logging.getLogger(__name__)


NoneType = type(None)

def _set_by_path_with_default(default=None):
    def _no_op(_, __, ___): 
        pass

    def _new_set_by_path(target_obj, target_path, value):
        print(f"DEFAULT value coming in {value}")
        if (isinstance(value, NoneType) or (value == "")) and default is not None:
            print("Setting value to {default}")
            return _set_by_path(target_obj, target_path, default)
        elif not isinstance(value, NoneType):
            print(f"Setting value to {value}")
            return _set_by_path(target_obj, target_path, value)
        else:
            return _no_op
    return _new_set_by_path

def _set_by_path(target_obj, target_path, value):
    if isinstance(value, NoneType):
        # pydash.set_(target_obj, target_path, "")
        pass
    else:
        pydash.set_(target_obj, target_path, value)

# def _set_by_path(target_obj, target_path, value):
#     """Set a (potentially nested) field in target_obj using JSONPath-esque dot notation, e.g. parent.child[0].field"""
#     pydash.set_(target_obj, target_path, value)


"""
Defines the parameters for extracting data from an Excel file and mapping it to a JSON object
"""
ExtractDataParams = namedtuple(
    "ExtractDataParams",
    ["field_mapping", "column_mapping", "meta_mapping", "section", "header_row"],
)


"""
Maps a named Excel cell to a JSON path with a callable that applies the cell value to the target object
"""
FieldMapping = dict[str, tuple[str, Callable[[Any, Any, Any], Any]]]

"""
Maps a named Excel column range to a JSON path with a callable that applies each cell value to the target object
"""
ColumnMapping = dict[str, tuple[str, str, Callable[[Any, Any, Any], Any]]]


def _extract_column(workbook, name):
    """Extacts a column of values from the workbook with the defined name"""
    definition = workbook.defined_names[name]

    for sheet_title, cell_coord in definition.destinations:
        sheet = workbook[sheet_title]
        cell_range = sheet[cell_coord]

        if not isinstance(cell_range, tuple):
            raise ExcelExtractionError(
                f"_extract_column expected cell_range to be type tuple, got {type(cell_range)}"
            )

        for cell in cell_range:
            if not isinstance(cell, tuple):
                raise ExcelExtractionError(
                    f"_extract_column expected cell to be type tuple, got {type(cell)}"
                )

            if not len(cell) == 1:
                raise ExcelExtractionError(
                    f"_extract_column expected tuple with length 1, got {len(cell)}"
                )

            if not isinstance(cell[0], Cell):
                raise ExcelExtractionError(
                    f"_extract_column expected type Cell, got {type(cell)}"
                )

            if cell[0].value is not None:
                # Return row number and value
                yield cell[0].row, cell[0].value


def _open_workbook(file):
    if isinstance(file, Workbook):
        return file
    else:
        return load_workbook(filename=file, data_only=True)


def _get_entries_by_path(dictionary, path):
    keys = path.split(".")
    val = dictionary
    for key in keys:
        try:
            val = val[key]
        except KeyError:
            return []
    return val


def _extract_single_value(workbook, name):
    """Extract a single value from the workbook with the defined name"""
    definition = workbook.defined_names[name]

    for sheet_title, cell_coord in definition.destinations:
        sheet = workbook[sheet_title]
        cell = sheet[cell_coord]

        if not isinstance(cell, Cell):
            raise ExcelExtractionError(
                f"_extract_single_value expected type Cell, got {type(cell)}"
            )

        return cell.value
    
def _extract_data(file, params: ExtractDataParams) -> dict:
    """
    Extracts data from an Excel file using provided field and column mappings
    """
    workbook = _open_workbook(file)
    result: dict = {}

    if SECTION_NAME not in workbook.defined_names:
        raise ExcelExtractionError(
            "The uploaded workbook template does not originate from SF-SAC.",
            error_key=UNKNOWN_WORKBOOK,
        )

    try:
        _extract_meta_and_field_data(workbook, params, result)
        if result.get("Meta", {}).get(SECTION_NAME) == params.section:
            _extract_column_data(workbook, result, params)
        return result

    except AttributeError as e:
        raise ExcelExtractionError(e)

def _extract_meta_and_field_data(workbook, params, result):
    for name, (target, set_fn) in params.meta_mapping.items():
        set_fn(result, target, _extract_single_value(workbook, name))

    if result.get("Meta", {}).get(SECTION_NAME) == params.section:
        for name, (target, set_fn) in params.field_mapping.items():
            set_fn(result, target, _extract_single_value(workbook, name))



def _extract_column_data(workbook, result, params):
    for i, (name, (parent_target, field_target, set_fn)) in enumerate(
        params.column_mapping.items()
    ):
        for row, value in _extract_column(workbook, name):
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


def _has_only_one_field_with_value_0(my_dict, field_name):
    """Check if the dictionary has exactly one field with the provided name and its value is 0"""
    return len(my_dict) == 1 and my_dict.get(field_name) == 0

def _remove_empty_award_entries(data):
    """Removes empty award entries from the data"""
    awards = []
    for award in data.get("FederalAwards", {}).get("federal_awards", []):
        if not all(
            [
                "direct_or_indirect_award" not in award,
                "loan_or_loan_guarantee" not in award,
                "subrecipients" not in award,
                "program" in award
                and _has_only_one_field_with_value_0(
                    award["program"], "federal_program_total"
                ),
                "cluster" in award
                and _has_only_one_field_with_value_0(award["cluster"], "cluster_total"),
            ]
        ):
            awards.append(award)
    if "FederalAwards" in data:
        # Update the federal_awards with the valid awards
        data["FederalAwards"]["federal_awards"] = awards

    return data

def _add_required_fields(data):
    """Adds empty parent fields to the json object to allow for proper schema validation / indexing"""
    indexed_awards = []
    for award in data.get("FederalAwards", {}).get("federal_awards", []):
        if "cluster" not in award:
            award["cluster"] = {}
        if "direct_or_indirect_award" not in award:
            award["direct_or_indirect_award"] = {}
        if "loan_or_loan_guarantee" not in award:
            award["loan_or_loan_guarantee"] = {}
        if "program" not in award:
            award["program"] = {}
        if "subrecipients" not in award:
            award["subrecipients"] = {}
        indexed_awards.append(award)

    if "FederalAwards" in data:
        # Update the federal_awards with all required fields
        data["FederalAwards"]["federal_awards"] = indexed_awards

    logger.info(data)

    return data

def _extract_from_column_mapping(path, row_index, column_mapping, match=None):
    """Extract named ranges from column mapping"""
    for key, value in column_mapping.items():
        if len(value) > 2 and (
            value[0] + "." + value[1] == path
            or (match and value[0] + "." + value[1] == path + "." + match.group(1))
        ):
            return key, row_index
    return None, None

def _extract_from_field_mapping(path, field_mapping, match=None):
    """Extract named ranges from field mapping"""
    for key, value in field_mapping.items():
        if len(value) == 2 and (
            value[0] == path or (match and value[0] == ".".join([path, match.group(1)]))
        ):
            return key, None
    return None, None

def _extract_error_details(error):
    if not bool(error.path):
        print("No path found in error object")
        return None, None, None
    row_index = next((item for item in error.path if isinstance(item, int)), None)
    path = ".".join([item for item in error.path if not isinstance(item, int)])
    match = re.search(r"'(\w+)'", error.message) if error.message else None
    return path, row_index, match

def _extract_key_from_award_entities(path, row_index, named_ranges):
    if path in [AWARD_ENTITY_NAME_PATH, AWARD_ENTITY_ID_PATH]:
        key = (
            AWARD_ENTITY_NAME_KEY
            if path == AWARD_ENTITY_NAME_PATH
            else AWARD_ENTITY_ID_KEY
        )
        named_ranges.append((key, row_index))
        return key
    return None

def _extract_named_ranges(errors, column_mapping, field_mapping, meta_mapping):
    """Extract named ranges from column mapping and errors"""
    named_ranges = []
    for error in errors:
        path, row_index, match = _extract_error_details(error)
        if not path:
            continue

        # Extract named ranges from column mapping for award entities
        keyFound = _extract_key_from_award_entities(path, row_index, named_ranges)

        if not keyFound:
            keyFound, row_index = _extract_from_column_mapping(
                path, row_index, column_mapping, match
            )
            if keyFound:
                named_ranges.append((keyFound, row_index))

        if not keyFound:
            keyFound, _ = _extract_from_field_mapping(path, field_mapping, match)
            if not keyFound:
                keyFound, _ = _extract_from_field_mapping(path, meta_mapping, match)
            if keyFound:
                named_ranges.append((keyFound, None))

        if not keyFound:
            print(f"No named range matches this error path: {error.path}")

    return named_ranges
