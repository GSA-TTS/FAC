import json
import logging
import json
import logging
from audit.fixtures.excel import (
    ADDITIONAL_EINS_TEMPLATE_DEFINITION,
    FORM_SECTIONS,
)

from .constants import (
    XLSX_TEMPLATE_DEFINITION_DIR,
)

from audit.fixtures.excel import (
    FORM_SECTIONS,
)

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

from .intermediate_representation import (
    extract_workbook_as_ir,
    _extract_generic_data,
)

from .checks import (
    run_all_general_checks,
    run_all_additional_eins_checks
    )

from .mapping_meta import meta_mapping

logger = logging.getLogger(__name__)


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

    ir = extract_workbook_as_ir(file)
    run_all_general_checks(ir, FORM_SECTIONS.ADDITIONAL_EINS)
    run_all_additional_eins_checks(ir)
    result = _extract_generic_data(ir, params)
    return result


def additional_eins_named_ranges(errors):
    return _extract_named_ranges(
        errors,
        additional_eins_column_mapping,
        additional_eins_field_mapping,
        meta_mapping,
    )


additional_eins_field_mapping: FieldMapping = {
    "auditee_uei": ("AdditionalEINs.auditee_uei", _set_by_path),
}

additional_eins_column_mapping: ColumnMapping = {
    "additional_ein": (
        "AdditionalEINs.additional_eins_entries",
        "additional_ein",
        _set_by_path,
    ),
}
