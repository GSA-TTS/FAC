import re
import json
from django.conf import settings
from typing import Any, Callable
from openpyxl import load_workbook, Workbook
from openpyxl.cell import Cell
from audit.fixtures.excel import (
    CORRECTIVE_ACTION_TEMPLATE_DEFINITION,
    FEDERAL_AWARDS_TEMPLATE_DEFINITION,
    FINDINGS_TEXT_TEMPLATE_DEFINITION,
    FINDINGS_UNIFORM_TEMPLATE_DEFINITION,
)
import pydash


AWARD_ENTITY_NAME_PATH = (
    "FederalAwards.federal_awards.direct_or_indirect_award.entities.passthrough_name"
)
AWARD_ENTITY_ID_PATH = "FederalAwards.federal_awards.direct_or_indirect_award.entities.passthrough_identifying_number"
AWARD_ENTITY_NAME_KEY = "passthrough_name"
AWARD_ENTITY_ID_KEY = "passthrough_identifying_number"
FEDERAL_AGENCY_PREFIX = "federal_agency_prefix"
THREE_DIGIT_EXTENSION = "three_digit_extension"

XLSX_TEMPLATE_DEFINITION_DIR = settings.XLSX_TEMPLATE_JSON_DIR


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
        _set_by_path(obj, f"{target}[{index}].passthrough_name", v)


def _set_pass_through_entity_id(obj, target, value):
    for index, v in enumerate(value.split("|")):
        _set_by_path(obj, f"{target}[{index}].passthrough_identifying_number", v)


federal_awards_field_mapping: FieldMapping = {
    "auditee_uei": ("FederalAwards.auditee_uei", _set_by_path),
    "total_amount_expended": ("FederalAwards.total_amount_expended", _set_by_path),
}
corrective_action_field_mapping: FieldMapping = {
    "auditee_uei": ("CorrectiveActionPlan.auditee_uei", _set_by_path),
}
findings_uniform_guidance_field_mapping: FieldMapping = {
    "auditee_uei": ("FindingsUniformGuidance.auditee_uei", _set_by_path),
}
findings_text_field_mapping: FieldMapping = {
    "auditee_uei": ("FindingsText.auditee_uei", _set_by_path),
}

federal_awards_column_mapping: ColumnMapping = {
    "federal_agency_prefix": (
        "FederalAwards.federal_awards",
        f"program.{FEDERAL_AGENCY_PREFIX}",
        _set_by_path,
    ),
    "three_digit_extension": (
        "FederalAwards.federal_awards",
        f"program.{THREE_DIGIT_EXTENSION}",
        _set_by_path,
    ),
    "additional_award_identification": (
        "FederalAwards.federal_awards",
        "program.additional_award_identification",
        _set_by_path,
    ),
    "program_name": (
        "FederalAwards.federal_awards",
        "program.program_name",
        _set_by_path,
    ),
    "amount_expended": (
        "FederalAwards.federal_awards",
        "program.amount_expended",
        _set_by_path,
    ),
    "cluster_name": (
        "FederalAwards.federal_awards",
        "cluster.cluster_name",
        _set_by_path,
    ),
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
    "federal_program_total": (
        "FederalAwards.federal_awards",
        "program.federal_program_total",
        _set_by_path,
    ),
    "cluster_total": (
        "FederalAwards.federal_awards",
        "cluster.cluster_total",
        _set_by_path,
    ),
    "is_guaranteed": (
        "FederalAwards.federal_awards",
        "loan_or_loan_guarantee.is_guaranteed",
        _set_by_path,
    ),
    "loan_balance_at_audit_period_end": (
        "FederalAwards.federal_awards",
        "loan_or_loan_guarantee.loan_balance_at_audit_period_end",
        _set_by_path,
    ),
    "is_direct": (
        "FederalAwards.federal_awards",
        "direct_or_indirect_award.is_direct",
        _set_by_path,
    ),
    AWARD_ENTITY_NAME_KEY: (
        "FederalAwards.federal_awards",
        "direct_or_indirect_award.entities",
        _set_pass_through_entity_name,
    ),
    AWARD_ENTITY_ID_KEY: (
        "FederalAwards.federal_awards",
        "direct_or_indirect_award.entities",
        _set_pass_through_entity_id,
    ),
    "is_passed": (
        "FederalAwards.federal_awards",
        "subrecipients.is_passed",
        _set_by_path,
    ),
    "subrecipient_amount": (
        "FederalAwards.federal_awards",
        "subrecipients.subrecipient_amount",
        _set_by_path,
    ),
    "is_major": ("FederalAwards.federal_awards", "program.is_major", _set_by_path),
    "audit_report_type": (
        "FederalAwards.federal_awards",
        "program.audit_report_type",
        _set_by_path,
    ),
    "number_of_audit_findings": (
        "FederalAwards.federal_awards",
        "program.number_of_audit_findings",
        _set_by_path,
    ),
}
corrective_action_column_mapping: ColumnMapping = {
    "reference_number": (
        "CorrectiveActionPlan.corrective_action_plan_entries",
        "reference_number",
        _set_by_path,
    ),
    "planned_action": (
        "CorrectiveActionPlan.corrective_action_plan_entries",
        "planned_action",
        _set_by_path,
    ),
    "contains_chart_or_table": (
        "CorrectiveActionPlan.corrective_action_plan_entries",
        "contains_chart_or_table",
        _set_by_path,
    ),
}
findings_uniform_guidance_column_mapping: ColumnMapping = {
    "federal_agency_prefix": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        f"program.{FEDERAL_AGENCY_PREFIX}",
        _set_by_path,
    ),
    "three_digit_extension": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        f"program.{THREE_DIGIT_EXTENSION}",
        _set_by_path,
    ),
    "additional_award_identification": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "program.additional_award_identification",
        _set_by_path,
    ),
    "program_name": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "program.program_name",
        _set_by_path,
    ),
    "reference_number": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "findings.reference_number",
        _set_by_path,
    ),
    "compliance_requirement": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "program.compliance_requirement",
        _set_by_path,
    ),
    "modified_opinion": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "modified_opinion",
        _set_by_path,
    ),
    "other_matters": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "other_matters",
        _set_by_path,
    ),
    "material_weakness": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "material_weakness",
        _set_by_path,
    ),
    "significant_deficiency": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "significant_deficiency",
        _set_by_path,
    ),
    "other_findings": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "other_findings",
        _set_by_path,
    ),
    "questioned_costs": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "questioned_costs",
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
}
findings_text_column_mapping: ColumnMapping = {
    "reference_number": (
        "FindingsText.findings_text_entries",
        "reference_number",
        _set_by_path,
    ),
    "text_of_finding": (
        "FindingsText.findings_text_entries",
        "text_of_finding",
        _set_by_path,
    ),
    "contains_chart_or_table": (
        "FindingsText.findings_text_entries",
        "contains_chart_or_table",
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


def _ensure_string_conversion(path, value):
    """
    This function checks whether the input path ends with certain specified suffixes,
    and if it does, it ensures the corresponding value is format as string.
    """
    if path.endswith(FEDERAL_AGENCY_PREFIX) or path.endswith(THREE_DIGIT_EXTENSION):
        return str(value)
    return value


def _extract_data(
    file,
    field_mapping: FieldMapping,
    column_mapping: ColumnMapping,
    header_row: int,
):
    """
    Extracts data from an Excel file using provided field and column mappings
    """
    result = {}  # type: dict[str, Any]

    workbook = _open_workbook(file)

    try:
        for name, (target, set_fn) in field_mapping.items():
            set_fn(result, target, _extract_single_value(workbook, name))

        for i, (name, (parent_target, field_target, set_fn)) in enumerate(
            column_mapping.items()
        ):
            row_value_pairs = list(_extract_column(workbook, name))
            for row, value in row_value_pairs:
                index = (row - header_row) - 1  # Subtract 1 to make it zero-indexed
                set_fn(
                    result,
                    f"{parent_target}[{index}].{field_target}",
                    _ensure_string_conversion(field_target, value),
                )

            # Necessary to prevent null entries when index/row is skipped in first column
            if i == 0:
                entries = [
                    entry if entry is not None else {}
                    for entry in _get_entries_by_path(result, parent_target)
                ]
                if entries:
                    set_fn(result, f"{parent_target}", entries)

    except AttributeError as e:
        raise ExcelExtractionError(e)

    return result


def extract_federal_awards(file):
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / FEDERAL_AWARDS_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    return _extract_data(
        file,
        federal_awards_field_mapping,
        federal_awards_column_mapping,
        template["title_row"],
    )


def extract_corrective_action_plan(file):
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / CORRECTIVE_ACTION_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    return _extract_data(
        file,
        corrective_action_field_mapping,
        corrective_action_column_mapping,
        template["title_row"],
    )


def extract_findings_uniform_guidance(file):
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / FINDINGS_UNIFORM_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    return _extract_data(
        file,
        findings_uniform_guidance_field_mapping,
        findings_uniform_guidance_column_mapping,
        template["title_row"],
    )


def extract_findings_text(file):
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / FINDINGS_TEXT_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    return _extract_data(
        file,
        findings_text_field_mapping,
        findings_text_column_mapping,
        template["title_row"],
    )


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


def _extract_named_ranges(errors, column_mapping, field_mapping):
    """Extract named ranges from column mapping and errors"""
    named_ranges = []
    for error in errors:
        if not bool(error.path):
            print("No path found in error object")
            continue
        print(error)
        keyFound = None
        match = None
        row_index = next((item for item in error.path if isinstance(item, int)), None)
        path = ".".join([item for item in error.path if not isinstance(item, int)])
        if error.message:
            match = re.search(r"'(\w+)'", error.message)

        # Extract named ranges from column mapping for award entities
        if path in [AWARD_ENTITY_NAME_PATH, AWARD_ENTITY_ID_PATH]:
            key = (
                AWARD_ENTITY_NAME_KEY
                if path == AWARD_ENTITY_NAME_PATH
                else AWARD_ENTITY_ID_KEY
            )
            named_ranges.append((key, row_index))
            keyFound = key

        if not keyFound:
            keyFound, row_index = _extract_from_column_mapping(
                path, row_index, column_mapping, match
            )
            if keyFound:
                named_ranges.append((keyFound, row_index))

        if not keyFound:
            keyFound, _ = _extract_from_field_mapping(path, field_mapping, match)
            if keyFound:
                named_ranges.append((keyFound, None))

        if not keyFound:
            print(f"No named range matches this error path: {error.path}")

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
