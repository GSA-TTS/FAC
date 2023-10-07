import json
import logging
import json
import logging
from audit.fixtures.excel import (
    FINDINGS_TEXT_TEMPLATE_DEFINITION,
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


def extract_audit_findings_text(file):
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
    return _extract_data(file, params)


def audit_findings_text_named_ranges(errors):
    return _extract_named_ranges(
        errors, audit_findings_text_column_mapping, audit_findings_text_field_mapping, meta_mapping
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
