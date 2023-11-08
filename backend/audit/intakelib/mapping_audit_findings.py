import json
import logging
from audit.fixtures.excel import (
    FINDINGS_UNIFORM_TEMPLATE_DEFINITION,
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
from .checks import run_all_general_checks, run_all_audit_finding_checks
from .transforms import run_all_audit_findings_transforms

logger = logging.getLogger(__name__)


def extract_audit_findings(file):
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / FINDINGS_UNIFORM_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    params = ExtractDataParams(
        audit_findings_field_mapping,
        audit_findings_column_mapping,
        meta_mapping,
        FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE,
        template["title_row"],
    )

    ir = extract_workbook_as_ir(file)
    run_all_general_checks(ir, FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE)
    xform_ir = run_all_audit_findings_transforms(ir)
    run_all_audit_finding_checks(xform_ir)
    result = _extract_generic_data(xform_ir, params)
    return result


def audit_findings_named_ranges(errors):
    return _extract_named_ranges(
        errors,
        audit_findings_field_mapping,
        audit_findings_column_mapping,
        meta_mapping,
    )


audit_findings_field_mapping: FieldMapping = {
    "auditee_uei": ("FindingsUniformGuidance.auditee_uei", _set_by_path),
}

audit_findings_column_mapping: ColumnMapping = {
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
