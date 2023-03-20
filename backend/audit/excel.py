from typing import Any, Callable
from openpyxl import load_workbook, Workbook
from openpyxl.cell import Cell
import pydash


def _set_by_path(target_obj, target_path, value):
    """Set a (potentially nested) field in target_obj using JSONPath-esque dot notation, e.g. parent.child[0].field"""
    pydash.set_(target_obj, target_path, value)


"""
Maps a named Excel cell to a JSON path with a callable that applies the cell value to the target object
"""
FieldMapping = dict[str, tuple[str, Callable[[Any, Any, Any], Any]]]

"""
Maps a named Excel column range to a JSON path with a callable that applies each cell value to the target object
"""
ColumnMapping = dict[str, tuple[str, str, Callable[[Any, Any, Any], Any]]]


def _set_pass_through_entity_name(obj, target, value):
    [
        _set_by_path(obj, f"{target}[{index}].name", v)
        for index, v in enumerate(value.split("|"))
    ]


def _set_pass_through_entity_id(obj, target, value):
    [
        _set_by_path(obj, f"{target}[{index}].identifying_number", v)
        for index, v in enumerate(value.split("|"))
    ]


federal_awards_field_mapping: FieldMapping = {
    "auditee_ein": ("FederalAwards.auditee_ein", _set_by_path),
    "total_amount_expended": ("FederalAwards.total_amount_expended", _set_by_path),
}

federal_awards_column_mapping: ColumnMapping = {
    "amount_expended": ("FederalAwards.federal_awards", "amount_expended", _set_by_path),
    "cluster_name": ("FederalAwards.federal_awards", "cluster_name", _set_by_path),
    "direct_award": ("FederalAwards.federal_awards", "direct_award", _set_by_path),
    "direct_award_pass_through_entity_name": (
        "FederalAwards.federal_awards",
        "direct_award_pass_through_entities",
        _set_pass_through_entity_name,
    ),
    "direct_award_pass_through_entity_id": (
        "FederalAwards.federal_awards",
        "direct_award_pass_through_entities",
        _set_pass_through_entity_id,
    ),
    "federal_award_passed_to_subrecipients": (
        "FederalAwards.federal_awards",
        "federal_award_passed_to_subrecipients",
        _set_by_path,
    ),
    "federal_award_passed_to_subrecipients_amount": (
        "FederalAwards.federal_awards",
        "federal_award_passed_to_subrecipients_amount",
        _set_by_path,
    ),
    "federal_program_name": (
        "FederalAwards.federal_awards",
        "federal_program_name",
        _set_by_path,
    ),
    "loan_balance_at_audit_period_end": (
        "FederalAwards.federal_awards",
        "loan_balance_at_audit_period_end",
        _set_by_path,
    ),
    "loan_or_loan_guarantee": (
        "FederalAwards.federal_awards",
        "loan_or_loan_guarantee",
        _set_by_path,
    ),
    "major_program": ("FederalAwards.federal_awards", "major_program", _set_by_path),
    "major_program_audit_report_type": (
        "FederalAwards.federal_awards",
        "major_program_audit_report_type",
        _set_by_path,
    ),
    "number_of_audit_findings": (
        "FederalAwards.federal_awards",
        "number_of_audit_findings",
        _set_by_path,
    ),
    "program_number": ("FederalAwards.federal_awards", "program_number", _set_by_path),
    "state_cluster_name": (
        "FederalAwards.federal_awards",
        "state_cluster_name",
        _set_by_path,
    ),
}


class ExcelExtractionError(Exception):
    pass


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
                yield cell[0].value


def _open_workbook(file):
    if isinstance(file, Workbook):
        return file
    else:
        return load_workbook(filename=file, data_only=True)


def extract_data(file, field_mapping: FieldMapping, column_mapping: ColumnMapping):
    """
    Extracts data from an Excel file using provided field and column mappings
    """
    result = {}  # type: dict[str, Any]

    workbook = _open_workbook(file)

    try:
        [
            set_fn(result, target, _extract_single_value(workbook, name))
            for name, (target, set_fn) in field_mapping.items()
        ]

        for name, (
            parent_target,
            field_target,
            set_fn,
        ) in column_mapping.items():
            [
                set_fn(result, f"{parent_target}[{index}].{field_target}", value)
                for index, value in enumerate(_extract_column(workbook, name))
            ]
    except AttributeError as e:
        raise ExcelExtractionError(e)

    return result


def extract_federal_awards(file):
    return extract_data(
        file, federal_awards_field_mapping, federal_awards_column_mapping
    )
