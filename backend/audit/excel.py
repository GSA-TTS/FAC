from collections import namedtuple
import re
import json
from django.conf import settings
from typing import Any, Callable
from openpyxl import load_workbook, Workbook
from openpyxl.cell import Cell
from audit.fixtures.excel import (
    ADDITIONAL_UEIS_TEMPLATE_DEFINITION,
    ADDITIONAL_EINS_TEMPLATE_DEFINITION,
    CORRECTIVE_ACTION_TEMPLATE_DEFINITION,
    FEDERAL_AWARDS_TEMPLATE_DEFINITION,
    FINDINGS_TEXT_TEMPLATE_DEFINITION,
    FINDINGS_UNIFORM_TEMPLATE_DEFINITION,
    SECONDARY_AUDITORS_TEMPLATE_DEFINITION,
    NOTES_TO_SEFA_TEMPLATE_DEFINITION,
    FORM_SECTIONS,
    UNKNOWN_WORKBOOK,
)
from audit.utils import ExcelExtractionError
import pydash


AWARD_ENTITY_NAME_PATH = (
    "FederalAwards.federal_awards.direct_or_indirect_award.entities.passthrough_name"
)
AWARD_ENTITY_ID_PATH = "FederalAwards.federal_awards.direct_or_indirect_award.entities.passthrough_identifying_number"
AWARD_ENTITY_NAME_KEY = "passthrough_name"
AWARD_ENTITY_ID_KEY = "passthrough_identifying_number"
FEDERAL_AGENCY_PREFIX = "federal_agency_prefix"
THREE_DIGIT_EXTENSION = "three_digit_extension"
SECTION_NAME = "section_name"
XLSX_TEMPLATE_DEFINITION_DIR = settings.XLSX_TEMPLATE_JSON_DIR

def _set_by_path(target_obj, target_path, value):
    """Set a (potentially nested) field in target_obj using JSONPath-esque dot notation, e.g. parent.child[0].field"""
    # IF a user:
    # * Prefixes a cell with a space
    # * Suffixes a cell with a space
    # * Enters only spaces (typically, just one...)
    # THEN
    # We do not want to set that value in the JSON object.
    # SO
    # We trim, and then check if we have "elimiated" the string.
    # If so, we pass. Do not modify the object.
    # Otherwise, set the object to the trimmed string.
    # We only do this for string values.
    if isinstance(value, str):
        value = value.strip()
        if value == "":
            pass
        else:
            pydash.set_(target_obj, target_path, value)
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


def _set_pass_through_entity_name(obj, target, value):
    for index, v in enumerate(value.split("|")):
        _set_by_path(obj, f"{target}[{index}].passthrough_name", v)


def _set_pass_through_entity_id(obj, target, value):
    for index, v in enumerate(value.split("|")):
        _set_by_path(obj, f"{target}[{index}].passthrough_identifying_number", v)


meta_mapping: FieldMapping = {
    SECTION_NAME: (f"Meta.{SECTION_NAME}", _set_by_path),
}
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
additional_ueis_field_mapping: FieldMapping = {
    "auditee_uei": ("AdditionalUEIs.auditee_uei", _set_by_path),
}
secondary_auditors_field_mapping: FieldMapping = {
    "auditee_uei": ("SecondaryAuditors.auditee_uei", _set_by_path),
}
notes_to_sefa_field_mapping: FieldMapping = {
    "auditee_uei": ("NotesToSefa.auditee_uei", _set_by_path),
    "accounting_policies": ("NotesToSefa.accounting_policies", _set_by_path),
    "is_minimis_rate_used": ("NotesToSefa.is_minimis_rate_used", _set_by_path),
    "rate_explained": ("NotesToSefa.rate_explained", _set_by_path),
}
additional_eins_field_mapping: FieldMapping = {
    "auditee_uei": ("AdditionalEINs.auditee_uei", _set_by_path),
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
    "award_reference": (
        "FederalAwards.federal_awards",
        "award_reference",
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
    "award_reference": (
        "FindingsUniformGuidance.findings_uniform_guidance_entries",
        "program.award_reference",
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
additional_ueis_column_mapping: ColumnMapping = {
    "additional_uei": (
        "AdditionalUEIs.additional_ueis_entries",
        "additional_uei",
        _set_by_path,
    ),
}
additional_eins_column_mapping: ColumnMapping = {
    "additional_ein": (
        "AdditionalEINs.additional_eins_entries",
        "additional_ein",
        _set_by_path,
    ),
}
secondary_auditors_column_mapping: ColumnMapping = {
    "secondary_auditor_name": (
        "SecondaryAuditors.secondary_auditors_entries",
        "secondary_auditor_name",
        _set_by_path,
    ),
    "secondary_auditor_ein": (
        "SecondaryAuditors.secondary_auditors_entries",
        "secondary_auditor_ein",
        _set_by_path,
    ),
    "secondary_auditor_address_street": (
        "SecondaryAuditors.secondary_auditors_entries",
        "secondary_auditor_address_street",
        _set_by_path,
    ),
    "secondary_auditor_address_city": (
        "SecondaryAuditors.secondary_auditors_entries",
        "secondary_auditor_address_city",
        _set_by_path,
    ),
    "secondary_auditor_address_state": (
        "SecondaryAuditors.secondary_auditors_entries",
        "secondary_auditor_address_state",
        _set_by_path,
    ),
    "secondary_auditor_address_zipcode": (
        "SecondaryAuditors.secondary_auditors_entries",
        "secondary_auditor_address_zipcode",
        _set_by_path,
    ),
    "secondary_auditor_contact_name": (
        "SecondaryAuditors.secondary_auditors_entries",
        "secondary_auditor_contact_name",
        _set_by_path,
    ),
    "secondary_auditor_contact_title": (
        "SecondaryAuditors.secondary_auditors_entries",
        "secondary_auditor_contact_title",
        _set_by_path,
    ),
    "secondary_auditor_contact_phone": (
        "SecondaryAuditors.secondary_auditors_entries",
        "secondary_auditor_contact_phone",
        _set_by_path,
    ),
    "secondary_auditor_contact_email": (
        "SecondaryAuditors.secondary_auditors_entries",
        "secondary_auditor_contact_email",
        _set_by_path,
    ),
}

notes_to_sefa_column_mapping: ColumnMapping = {
    "note_title": (
        "NotesToSefa.notes_to_sefa_entries",
        "note_title",
        _set_by_path,
    ),
    "note_content": (
        "NotesToSefa.notes_to_sefa_entries",
        "note_content",
        _set_by_path,
    ),
    "contains_chart_or_table": (
        "NotesToSefa.notes_to_sefa_entries",
        "contains_chart_or_table",
        _set_by_path,
    ),
    "seq_number": (
        "NotesToSefa.notes_to_sefa_entries",
        "seq_number",
        _set_by_path,
    ),
}


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

    print(data)

    return data


def extract_federal_awards(file):
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / FEDERAL_AWARDS_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    params = ExtractDataParams(
        federal_awards_field_mapping,
        federal_awards_column_mapping,
        meta_mapping,
        FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED,
        template["title_row"],
    )
    result = _extract_data(file, params)
    result = _remove_empty_award_entries(result)
    result = _add_required_fields(result)
    return result


def extract_corrective_action_plan(file):
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / CORRECTIVE_ACTION_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    params = ExtractDataParams(
        corrective_action_field_mapping,
        corrective_action_column_mapping,
        meta_mapping,
        FORM_SECTIONS.CORRECTIVE_ACTION_PLAN,
        template["title_row"],
    )
    return _extract_data(file, params)


def extract_findings_uniform_guidance(file):
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / FINDINGS_UNIFORM_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    params = ExtractDataParams(
        findings_uniform_guidance_field_mapping,
        findings_uniform_guidance_column_mapping,
        meta_mapping,
        FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE,
        template["title_row"],
    )
    return _extract_data(file, params)


def extract_findings_text(file):
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / FINDINGS_TEXT_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    params = ExtractDataParams(
        findings_text_field_mapping,
        findings_text_column_mapping,
        meta_mapping,
        FORM_SECTIONS.FINDINGS_TEXT,
        template["title_row"],
    )
    return _extract_data(file, params)


def extract_additional_ueis(file):
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / ADDITIONAL_UEIS_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    params = ExtractDataParams(
        additional_ueis_field_mapping,
        additional_ueis_column_mapping,
        meta_mapping,
        FORM_SECTIONS.ADDITIONAL_UEIS,
        template["title_row"],
    )
    return _extract_data(file, params)


def extract_additional_eins(file):
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / ADDITIONAL_EINS_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    params = ExtractDataParams(
        additional_eins_field_mapping,
        additional_eins_column_mapping,
        meta_mapping,
        FORM_SECTIONS.ADDITIONAL_EINS,
        template["title_row"],
    )
    return _extract_data(file, params)


def extract_secondary_auditors(file):
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / SECONDARY_AUDITORS_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    params = ExtractDataParams(
        secondary_auditors_field_mapping,
        secondary_auditors_column_mapping,
        meta_mapping,
        FORM_SECTIONS.SECONDARY_AUDITORS,
        template["title_row"],
    )
    return _extract_data(file, params)


def extract_notes_to_sefa(file):
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / NOTES_TO_SEFA_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    params = ExtractDataParams(
        notes_to_sefa_field_mapping,
        notes_to_sefa_column_mapping,
        meta_mapping,
        FORM_SECTIONS.NOTES_TO_SEFA,
        template["title_row"],
    )
    return _extract_data(file, params)


def _extract_from_column_mapping(path, row_index, column_mapping, field_name=None):
    """Extract named ranges from column mapping"""
    for key, value in column_mapping.items():
        if len(value) > 2 and (
            value[0] + "." + value[1] == path
            or (field_name and value[0] + "." + value[1] == path + "." + field_name)
        ):
            return key, row_index
    return None, None


def _extract_from_field_mapping(path, field_mapping, field_name=None):
    """Extract named ranges from field mapping"""
    for key, value in field_mapping.items():
        if len(value) == 2 and (
            value[0] == path
            or (field_name and value[0] == ".".join([path, field_name]))
        ):
            return key, None
    return None, None


def _extract_error_details(error):
    if not bool(error.path):
        print("No path found in error object")
        return None, None, None
    row_index = next((item for item in error.path if isinstance(item, int)), None)
    path = ".".join([item for item in error.path if not isinstance(item, int)])
    return path, row_index


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


def _extract_validation_field_name(error):
    try:
        # Parse the input data as JSON
        data_dict = error.schema
        # Check if the input data is in the format { ... 'not': {'required': ['field_name']}}
        if "not" in data_dict and "required" in data_dict["not"]:
            field_name = data_dict["not"]["required"][0]
        # Check if the input data is in the format {...'required': ['field_name']}
        elif "required" in data_dict:
            field_name = data_dict["required"][0]
        else:
            match = re.search(r"'(\w+)'", error.message) if error.message else None
            field_name = match.group(1) if match else None
        return field_name
    except json.JSONDecodeError:
        return None


def _extract_named_ranges(errors, column_mapping, field_mapping, meta_mapping):
    """Extract named ranges from column mapping and errors"""
    named_ranges = []
    for error in errors:
        path, row_index = _extract_error_details(error)
        field_name = _extract_validation_field_name(error)
        if not path:
            continue

        # Extract named ranges from column mapping for award entities
        keyFound = _extract_key_from_award_entities(path, row_index, named_ranges)

        if not keyFound:
            keyFound, row_index = _extract_from_column_mapping(
                path, row_index, column_mapping, field_name
            )
            if keyFound:
                named_ranges.append((keyFound, row_index))

        if not keyFound:
            keyFound, _ = _extract_from_field_mapping(path, field_mapping, field_name)
            if not keyFound:
                keyFound, _ = _extract_from_field_mapping(
                    path, meta_mapping, field_name
                )
            if keyFound:
                named_ranges.append((keyFound, None))

        if not keyFound:
            print(f"No named range matches this error path: {error.path}")

    return named_ranges


def corrective_action_plan_named_ranges(errors):
    return _extract_named_ranges(
        errors,
        corrective_action_column_mapping,
        corrective_action_field_mapping,
        meta_mapping,
    )


def federal_awards_named_ranges(errors):
    return _extract_named_ranges(
        errors,
        federal_awards_column_mapping,
        federal_awards_field_mapping,
        meta_mapping,
    )


def findings_uniform_guidance_named_ranges(errors):
    return _extract_named_ranges(
        errors,
        findings_uniform_guidance_column_mapping,
        findings_uniform_guidance_field_mapping,
        meta_mapping,
    )


def findings_text_named_ranges(errors):
    return _extract_named_ranges(
        errors, findings_text_column_mapping, findings_text_field_mapping, meta_mapping
    )


def additional_ueis_named_ranges(errors):
    return _extract_named_ranges(
        errors,
        additional_ueis_column_mapping,
        additional_ueis_field_mapping,
        meta_mapping,
    )


def additional_eins_named_ranges(errors):
    return _extract_named_ranges(
        errors,
        additional_eins_column_mapping,
        additional_eins_field_mapping,
        meta_mapping,
    )


def secondary_auditors_named_ranges(errors):
    return _extract_named_ranges(
        errors,
        secondary_auditors_column_mapping,
        secondary_auditors_field_mapping,
        meta_mapping,
    )


def notes_to_sefa_named_ranges(errors):
    return _extract_named_ranges(
        errors, notes_to_sefa_column_mapping, notes_to_sefa_field_mapping, meta_mapping
    )
