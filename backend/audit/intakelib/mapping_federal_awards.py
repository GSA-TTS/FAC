import json
import logging
import json
import logging
import pprint
from audit.fixtures.excel import (
    FEDERAL_AWARDS_TEMPLATE_DEFINITION,
    FORM_SECTIONS,
)

from audit.fixtures.excel import (
    FEDERAL_AWARDS_TEMPLATE_DEFINITION,
    FORM_SECTIONS,
)

from .constants import (    
    XLSX_TEMPLATE_DEFINITION_DIR,
    FEDERAL_AGENCY_PREFIX,
    THREE_DIGIT_EXTENSION,
    AWARD_ENTITY_ID_KEY,
    AWARD_ENTITY_NAME_KEY
)

from .mapping_util import (
    _set_by_path,
    _set_pass_through_entity_name,
    _set_pass_through_entity_id,
    _set_by_path_with_default,
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

logger = logging.getLogger(__name__)
def extract_federal_awards(file):
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / FEDERAL_AWARDS_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    
    workbook = extract_workbook_as_ir(file)
    pprint.pprint(workbook)
    params = ExtractDataParams(
        federal_awards_field_mapping,
        federal_awards_column_mapping,
        meta_mapping,
        FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED,
        template["title_row"],
    )
    result = _extract_generic_data(workbook, params)
    pprint.pprint(result, indent=2, width=80)
    return result


def federal_awards_named_ranges(errors):
    return _extract_named_ranges(
        errors,
        federal_awards_column_mapping,
        federal_awards_field_mapping,
        meta_mapping,
    )

new_federal_awards_field_mapping: FieldMapping = {
    "auditee_uei": ("FederalAwards.auditee_uei", _set_by_path),
    "total_amount_expended": ("FederalAwards.total_amount_expended", _set_by_path),
}

federal_awards_field_mapping: FieldMapping = {
    "auditee_uei": ("FederalAwards.auditee_uei", _set_by_path),
    "total_amount_expended": ("FederalAwards.total_amount_expended", _set_by_path),
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
        _set_by_path_with_default(0),
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
