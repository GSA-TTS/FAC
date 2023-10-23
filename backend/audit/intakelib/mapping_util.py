from collections import namedtuple
import pydash
import re
from typing import Any, Callable
import logging
from openpyxl import load_workbook, Workbook

from .constants import (
    AWARD_ENTITY_NAME_PATH,
    AWARD_ENTITY_NAME_KEY,
    AWARD_ENTITY_ID_PATH,
    AWARD_ENTITY_ID_KEY,
)


logger = logging.getLogger(__name__)


def _set_by_path_with_default(default=None):
    def _no_op(_, __, ___):
        pass

    def _new_set_by_path(target_obj, target_path, value):
        if (value is None or value == "") and default is not None:
            return _set_by_path(target_obj, target_path, default)
        elif value is not None:
            return _set_by_path(target_obj, target_path, value)
        else:
            return _no_op

    return _new_set_by_path


def _set_by_path(target_obj, target_path, value):
    if value is None:
        pass
    else:
        pydash.set_(target_obj, target_path, value)


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


def _open_workbook(file):
    if isinstance(file, Workbook):
        return file
    else:
        wb = None
        wb = load_workbook(filename=file, data_only=True)
        return wb


def _get_entries_by_path(dictionary, path):
    keys = path.split(".")
    val = dictionary
    for key in keys:
        try:
            val = val[key]
        except KeyError:
            return []
    return val


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
        logger.info("No path found in error object")
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
            logger.info(f"No named range matches this error path: {error.path}")

    return named_ranges
