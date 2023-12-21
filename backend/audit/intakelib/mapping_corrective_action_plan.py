import json
import logging
from audit.fixtures.excel import (
    CORRECTIVE_ACTION_TEMPLATE_DEFINITION,
    FORM_SECTIONS,
)

from .constants import XLSX_TEMPLATE_DEFINITION_DIR

from .intermediate_representation import (
    extract_workbook_as_ir,
    _extract_generic_data,
)

from .mapping_util import (
    _set_by_path,
    FieldMapping,
    ColumnMapping,
    ExtractDataParams,
    _extract_named_ranges,
)

from .mapping_meta import meta_mapping
from .checks import run_all_general_checks, run_all_corrective_action_plan_checks
from .transforms import run_all_corrective_action_plan_transforms

logger = logging.getLogger(__name__)


def extract_corrective_action_plan(file, is_gsa_migration=False):
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

    ir = extract_workbook_as_ir(file)
    run_all_general_checks(ir, FORM_SECTIONS.CORRECTIVE_ACTION_PLAN, is_gsa_migration)
    xform_ir = run_all_corrective_action_plan_transforms(ir)
    run_all_corrective_action_plan_checks(xform_ir, is_gsa_migration)
    result = _extract_generic_data(xform_ir, params)
    return result


def corrective_action_plan_named_ranges(errors):
    return _extract_named_ranges(
        errors,
        corrective_action_column_mapping,
        corrective_action_field_mapping,
        meta_mapping,
    )


corrective_action_field_mapping: FieldMapping = {
    "auditee_uei": ("CorrectiveActionPlan.auditee_uei", _set_by_path),
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
