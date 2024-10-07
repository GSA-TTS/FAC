import json
import logging
import os
from audit.fixtures.excel import (
    FINDINGS_TEXT_TEMPLATE_DEFINITION,
    FORM_SECTIONS,
)

from .constants import XLSX_TEMPLATE_DEFINITION_DIR

from .mapping_util import (
    _set_by_path,
    FieldMapping,
    ColumnMapping,
    ExtractDataParams,
    _extract_named_ranges,
)

from .intermediate_representation import (
    extract_workbook_as_ir,
    _extract_generic_data,
)

from .mapping_meta import meta_mapping
from .transforms import run_all_audit_findings_text_transforms
from .checks import run_all_general_checks, run_all_audit_findings_text_checks

logger = logging.getLogger(__name__)


def extract_audit_findings_text(file, is_gsa_migration=False, auditee_uei=None):
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / FINDINGS_TEXT_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    params = ExtractDataParams(
        audit_findings_text_field_mapping,
        audit_findings_text_column_mapping,
        meta_mapping,
        FORM_SECTIONS.FINDINGS_TEXT,
        template["title_row"],
    )

    _, file_extension = os.path.splitext(file)
    if file_extension == ".xlsx":
        ir = extract_workbook_as_ir(file)
    elif file_extension == ".json":
        try:
            with open(file, "r", encoding="utf-8") as f:
                ir = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Error loading JSON file {file}: {e}")
    else:
        raise ValueError("File must be a JSON file or an XLSX file")
    
    run_all_general_checks(
        ir, FORM_SECTIONS.FINDINGS_TEXT, is_gsa_migration, auditee_uei
    )
    xform_ir = run_all_audit_findings_text_transforms(ir)
    run_all_audit_findings_text_checks(xform_ir, is_gsa_migration)
    result = _extract_generic_data(xform_ir, params)
    return result


def audit_findings_text_named_ranges(errors):
    return _extract_named_ranges(
        errors,
        audit_findings_text_column_mapping,
        audit_findings_text_field_mapping,
        meta_mapping,
    )


audit_findings_text_field_mapping: FieldMapping = {
    "auditee_uei": ("FindingsText.auditee_uei", _set_by_path),
}

audit_findings_text_column_mapping: ColumnMapping = {
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
