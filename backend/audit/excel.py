from openpyxl import load_workbook, Workbook
from openpyxl.cell import Cell
import pydash


def _set_pass_through_entity_name(obj, target, value):
    [
        pydash.set_(obj, f"{target}[{index}].name", v)
        for index, v in enumerate(value.split("|"))
    ]


def _set_pass_through_entity_id(obj, target, value):
    [
        pydash.set_(obj, f"{target}[{index}].identifying_number", v)
        for index, v in enumerate(value.split("|"))
    ]


federal_awards_mapping_single = {
    "auditee_ein": ("FederalAwards.auditee_ein", pydash.set_),
    "total_amount_expended": ("FederalAwards.total_amount_expended", pydash.set_),
}

federal_awards_mapping_column = {
    "amount_expended": ("FederalAwards.federal_awards", "amount_expended", pydash.set_),
    "cluster_name": ("FederalAwards.federal_awards", "cluster_name", pydash.set_),
    "direct_award": ("FederalAwards.federal_awards", "direct_award", pydash.set_),
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
        pydash.set_,
    ),
    "federal_award_passed_to_subrecipients_amount": (
        "FederalAwards.federal_awards",
        "federal_award_passed_to_subrecipients_amount",
        pydash.set_,
    ),
    "federal_program_name": (
        "FederalAwards.federal_awards",
        "federal_program_name",
        pydash.set_,
    ),
    "loan_balance_at_audit_period_end": (
        "FederalAwards.federal_awards",
        "loan_balance_at_audit_period_end",
        pydash.set_,
    ),
    "loan_or_loan_guarantee": (
        "FederalAwards.federal_awards",
        "loan_or_loan_guarantee",
        pydash.set_,
    ),
    "major_program": ("FederalAwards.federal_awards", "major_program", pydash.set_),
    "major_program_audit_report_type": (
        "FederalAwards.federal_awards",
        "major_program_audit_report_type",
        pydash.set_,
    ),
    "number_of_audit_findings": (
        "FederalAwards.federal_awards",
        "number_of_audit_findings",
        pydash.set_,
    ),
    "program_number": ("FederalAwards.federal_awards", "program_number", pydash.set_),
    "state_cluster_name": (
        "FederalAwards.federal_awards",
        "state_cluster_name",
        pydash.set_,
    ),
}


def _extract_single_value(workbook, name):
    """Extract a single value from the workbook with the defined name"""
    definition = workbook.defined_names[name]

    for sheet_title, cell_coord in definition.destinations:
        sheet = workbook[sheet_title]
        cell = sheet[cell_coord]

        if not isinstance(cell, Cell):
            raise TypeError("_extract_single_value expected type Cell")

        return cell.value


def _extract_column(workbook, name):
    """Extacts a column of values from the workbook with the defined name"""
    definition = workbook.defined_names[name]

    for sheet_title, cell_coord in definition.destinations:
        sheet = workbook[sheet_title]
        cell_range = sheet[cell_coord]

        for cell in cell_range:
            if cell[0].value is not None:
                yield cell[0].value


def _open_workbook(file):
    if isinstance(file, Workbook):
        return file
    else:
        return load_workbook(filename=file, data_only=True)


def extract_federal_awards(file):
    result = {}

    workbook = _open_workbook(file)

    [
        set_fn(result, target, _extract_single_value(workbook, name))
        for name, (target, set_fn) in federal_awards_mapping_single.items()
    ]

    for name, (
        parent_target,
        field_target,
        set_fn,
    ) in federal_awards_mapping_column.items():
        [
            set_fn(result, f"{parent_target}[{index}].{field_target}", value)
            for index, value in enumerate(_extract_column(workbook, name))
        ]

    return result
