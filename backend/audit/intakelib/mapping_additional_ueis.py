import json
import logging
import json
import logging
from audit.fixtures.excel import (
    ADDITIONAL_UEIS_TEMPLATE_DEFINITION,
    FORM_SECTIONS,
)

from .constants import (
    XLSX_TEMPLATE_DEFINITION_DIR
)

from audit.fixtures.excel import (
    FORM_SECTIONS,
)

from .mapping_util import (
    _set_by_path,
    FieldMapping,
    ColumnMapping,
    ExtractDataParams,
    _extract_named_ranges,
    _extract_data
)
from .mapping_meta import meta_mapping

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
    return _extract_data(file, params)

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
