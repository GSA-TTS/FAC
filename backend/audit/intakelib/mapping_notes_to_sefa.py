import json
import logging
from audit.fixtures.excel import (
    NOTES_TO_SEFA_TEMPLATE_DEFINITION,
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
from .checks import run_all_general_checks, run_all_notes_to_sefa_checks
from .transforms import run_all_notes_to_sefa_transforms


logger = logging.getLogger(__name__)


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

    ir = extract_workbook_as_ir(file)
    run_all_general_checks(ir, FORM_SECTIONS.NOTES_TO_SEFA)
    print("Done running all general checks")
    new_ir = run_all_notes_to_sefa_transforms(ir)
    run_all_notes_to_sefa_checks(new_ir)
    result = _extract_generic_data(new_ir, params)
    return result


def notes_to_sefa_named_ranges(errors):
    return _extract_named_ranges(
        errors, notes_to_sefa_column_mapping, notes_to_sefa_field_mapping, meta_mapping
    )


notes_to_sefa_field_mapping: FieldMapping = {
    "auditee_uei": ("NotesToSefa.auditee_uei", _set_by_path),
    "accounting_policies": ("NotesToSefa.accounting_policies", _set_by_path),
    "is_minimis_rate_used": ("NotesToSefa.is_minimis_rate_used", _set_by_path),
    "rate_explained": ("NotesToSefa.rate_explained", _set_by_path),
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
