import json
import logging

from audit.fixtures.excel import (
    ADDITIONAL_UEIS_TEMPLATE_DEFINITION,
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
from .transforms import run_all_additional_ueis_transforms
from .checks import run_all_general_checks, run_all_additional_ueis_checks

logger = logging.getLogger(__name__)


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

    ir = extract_workbook_as_ir(file)
    run_all_general_checks(ir, FORM_SECTIONS.ADDITIONAL_UEIS)
    xform_ir = run_all_additional_ueis_transforms(ir)
    run_all_additional_ueis_checks(xform_ir)
    result = _extract_generic_data(xform_ir, params)
    return result


def additional_ueis_named_ranges(errors):
    return _extract_named_ranges(
        errors,
        additional_ueis_column_mapping,
        additional_ueis_field_mapping,
        meta_mapping,
    )


additional_ueis_field_mapping: FieldMapping = {
    "auditee_uei": ("AdditionalUEIs.auditee_uei", _set_by_path),
}

additional_ueis_column_mapping: ColumnMapping = {
    "additional_uei": (
        "AdditionalUEIs.additional_ueis_entries",
        "additional_uei",
        _set_by_path,
    ),
}
