import re
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
    for index, v in enumerate(value.split("|")):
        _set_by_path(obj, f"{target}[{index}].name", v)


def _set_pass_through_entity_id(obj, target, value):
    for index, v in enumerate(value.split("|")):
        _set_by_path(obj, f"{target}[{index}].identifying_number", v)


federal_awards_field_mapping: FieldMapping = {
    "auditee_ein": ("FederalAwards.auditee_ein", _set_by_path),
    "total_amount_expended": ("FederalAwards.total_amount_expended", _set_by_path),
}
corrective_action_field_mapping: FieldMapping = {
    "auditee_ein": ("CorrectiveActionPlan.auditee_ein", _set_by_path),
}
findings_uniform_guidance_field_mapping: FieldMapping = {
    "auditee_ein": ("FindingsUniformGuidance.auditee_ein", _set_by_path),
}
findings_text_field_mapping: FieldMapping = {
    "auditee_ein": ("FindingsText.auditee_ein", _set_by_path),
}

federal_awards_column_mapping: ColumnMapping = {
    "amount_expended": (
        "FederalAwards.federal_awards",
        "amount_expended",
        _set_by_path,
    ),
    "cluster_name": ("FederalAwards.federal_awards", "cluster.name", _set_by_path),
    # 20230410 MCJ FIXME: I don't think we extract the cluster total?
    # Perhaps it is lacking a named range?
    # "cluster_total": ("FederalAwards.federal_awards", "cluster.total", _set_by_path),
    "direct_award": (
        "FederalAwards.federal_awards",
        "direct_or_indirect_award.is_direct",
        _set_by_path,
    ),
    "direct_award_pass_through_entity_name": (
        "FederalAwards.federal_awards",
        "direct_or_indirect_award.entities",
        _set_pass_through_entity_name,
    ),
    "direct_award_pass_through_entity_id": (
        "FederalAwards.federal_awards",
        "direct_or_indirect_award.entities",
        _set_pass_through_entity_id,
    ),
    "federal_award_passed_to_subrecipients": (
        "FederalAwards.federal_awards",
        "subrecipients.is_passed",
        _set_by_path,
    ),
    "federal_award_passed_to_subrecipients_amount": (
        "FederalAwards.federal_awards",
        "subrecipients.amount",
        _set_by_path,
    ),
    "federal_program_name": (
        "FederalAwards.federal_awards",
        "program.name",
        _set_by_path,
    ),
    "loan_balance_at_audit_period_end": (
        "FederalAwards.federal_awards",
        "loan_or_loan_guarantee.loan_balance_at_audit_period_end",
        _set_by_path,
    ),
    "loan_or_loan_guarantee": (
        "FederalAwards.federal_awards",
        "loan_or_loan_guarantee.is_guaranteed",
        _set_by_path,
    ),
    "major_program": ("FederalAwards.federal_awards", "program.is_major", _set_by_path),
    "major_program_audit_report_type": (
        "FederalAwards.federal_awards",
        "program.audit_report_type",
        _set_by_path,
    ),
    "number_of_audit_findings": (
        "FederalAwards.federal_awards",
        "program.number_of_audit_findings",
        _set_by_path,
    ),
    "program_number": ("FederalAwards.federal_awards", "program.number", _set_by_path),
    "state_cluster_name": (
        "FederalAwards.federal_awards",
        "cluster.state_cluster_name",
        _set_by_path,
    ),
    "other_cluster_name": (
        "FederalAwards.federal_awards",
        "cluster.other_cluster_name",
        _set_by_path,
    ),
}
corrective_action_column_mapping: ColumnMapping = {
    "contains_chart_or_table": (
        "CorrectiveActionPlan.corrective_action_plan_entries",
        "contains_chart_or_table",
        _set_by_path,
    ),
    "planned_action": (
        "CorrectiveActionPlan.corrective_action_plan_entries",
        "planned_action",
        _set_by_path,
    ),
    "reference_number": (
        "CorrectiveActionPlan.corrective_action_plan_entries",
        "reference_number",
        _set_by_path,
    ),
}
findings_uniform_guidance_column_mapping: ColumnMapping = {
    "program_number": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "program.number",
        _set_by_path,
    ),
    "program_name": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "program.name",
        _set_by_path,
    ),
    "compliance_requirement": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "program.compliance_requirement",
        _set_by_path,
    ),
    "finding_reference_number": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "findings.reference",
        _set_by_path,
    ),
    "repeat_prior_reference": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "findings.repeat_prior_reference",
        _set_by_path,
    ),
    "prior_references": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "findings.prior_references",
        _set_by_path,
    ),
    "is_valid": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "findings.is_valid",
        _set_by_path,
    ),
    "questioned_costs": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "questioned_costs",
        _set_by_path,
    ),
    "significiant_deficiency": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "significiant_deficiency",
        _set_by_path,
    ),
    "other_matters": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "other_matters",
        _set_by_path,
    ),
    "other_findings": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "other_findings",
        _set_by_path,
    ),
    "modified_opinion": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "modified_opinion",
        _set_by_path,
    ),
    "material_weakness": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "material_weakness",
        _set_by_path,
    ),
}
findings_text_column_mapping: ColumnMapping = {
    "reference_number": (
        "FindingsText.findings_text_entries",
        "reference_number",
        _set_by_path,
    ),
    "contains_chart_or_table": (
        "FindingsText.findings_text_entries",
        "contains_chart_or_table",
        _set_by_path,
    ),
    "text_of_finding": (
        "FindingsText.findings_text_entries",
        "text_of_finding",
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
        for name, (target, set_fn) in field_mapping.items():
            set_fn(result, target, _extract_single_value(workbook, name))

        for name, (parent_target, field_target, set_fn) in column_mapping.items():
            for index, value in enumerate(_extract_column(workbook, name)):
                set_fn(result, f"{parent_target}[{index}].{field_target}", value)

    except AttributeError as e:
        raise ExcelExtractionError(e)

    return result


def extract_federal_awards(file):
    return extract_data(
        file, federal_awards_field_mapping, federal_awards_column_mapping
    )


def extract_corrective_action_plan(file):
    return extract_data(
        file, corrective_action_field_mapping, corrective_action_column_mapping
    )


def extract_findings_uniform_guidance(file):
    return extract_data(
        file,
        findings_uniform_guidance_field_mapping,
        findings_uniform_guidance_column_mapping,
    )


def extract_findings_text(file):
    return extract_data(file, findings_text_field_mapping, findings_text_column_mapping)


def _extract_named_ranges(errors, column_mapping, field_mapping):
    """Extract named ranges from column mapping and errors"""
    named_ranges = []
    for error in errors:
        if bool(error.path):
            # This works because we only expecting a single index in error.path for all column mappings except for two egde cases
            row_index = next(
                (item for item in error.path if isinstance(item, int)), None
            )
            path = ".".join([item for item in error.path if not isinstance(item, int)])

            # Extract named ranges from column mapping
            for key, value in column_mapping.items():
                if len(value) > 2 and value[0] + "." + value[1] == path:
                    named_ranges.append((key, row_index))
                    break
            # Extract named ranges from field mapping
            for key, value in field_mapping.items():
                if (
                    len(value) == 2
                    and error.message
                    and value[0]
                    == ".".join([path, re.search(r"'(\w+)'", error.message).group(1)])
                ):
                    named_ranges.append((key, None))
                    break

        else:
            print("No path found in error object")
    return named_ranges


def corrective_action_plan_named_ranges(errors):
    return _extract_named_ranges(
        errors, corrective_action_column_mapping, corrective_action_field_mapping
    )


def federal_awards_named_ranges(errors):
    return _extract_named_ranges(
        errors, federal_awards_column_mapping, federal_awards_field_mapping
    )


def findings_uniform_guidance_named_ranges(errors):
    return _extract_named_ranges(
        errors,
        findings_uniform_guidance_column_mapping,
        findings_uniform_guidance_field_mapping,
    )


def findings_text_named_ranges(errors):
    return _extract_named_ranges(
        errors, findings_text_column_mapping, findings_text_field_mapping
    )
