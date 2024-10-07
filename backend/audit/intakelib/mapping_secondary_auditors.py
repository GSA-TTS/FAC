import json
import logging
import os
from audit.fixtures.excel import (
    SECONDARY_AUDITORS_TEMPLATE_DEFINITION,
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

from .mapping_meta import meta_mapping

from .checks import run_all_general_checks, run_all_secondary_auditors_checks
from .transforms import run_all_secondary_auditors_transforms
from .intermediate_representation import (
    extract_workbook_as_ir,
    _extract_generic_data,
)

logger = logging.getLogger(__name__)


def extract_secondary_auditors(file, is_gsa_migration=False, auditee_uei=None):
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
        ir, FORM_SECTIONS.SECONDARY_AUDITORS, is_gsa_migration, auditee_uei
    )
    xform_ir = run_all_secondary_auditors_transforms(ir)
    run_all_secondary_auditors_checks(xform_ir, is_gsa_migration)
    result = _extract_generic_data(xform_ir, params)
    return result


def secondary_auditors_named_ranges(errors):
    return _extract_named_ranges(
        errors,
        secondary_auditors_column_mapping,
        secondary_auditors_field_mapping,
        meta_mapping,
    )


secondary_auditors_field_mapping: FieldMapping = {
    "auditee_uei": ("SecondaryAuditors.auditee_uei", _set_by_path),
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
