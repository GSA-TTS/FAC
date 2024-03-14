from django.core.exceptions import ValidationError
import logging
from audit.intakelib.common import get_missing_value_errors
from audit.fixtures.excel import FORM_SECTIONS

logger = logging.getLogger(__name__)

map_required_field_ranges_to_workbook = {
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: {
        "award_reference": "check_missing_award_numbers",
        "federal_agency_prefix": "check_missing_federal_agency_prefix",
        "three_digit_extension": "check_missing_aln_three_digit_extension",
        "program_name": "check_missing_program_name",
        "amount_expended": "check_missing_amount_expended",
        "cluster_name": "check_missing_cluster_name",
        "federal_program_total": "check_missing_federal_program_total",
        "cluster_total": "check_missing_cluster_total",
        "is_guaranteed": "check_missing_loan_guaranteed",
        "is_direct": "check_direct_award_is_not_blank",
        "is_passed": "check_federal_award_passed_always_present",
        "is_major": "check_no_major_program_is_blank",
        "number_of_audit_findings": "check_num_findings_always_present",
    },
    # This will not prevent user for submitting an empty workbook as long as the coversheet is filled out.
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: {
        "award_reference": "check_missing_award_numbers",
        "reference_number": "check_missing_reference_numbers",
        "compliance_requirement": "check_missing_compliance_requirement",
        "modified_opinion": "check_missing_modified_opinion",
        "other_matters": "check_missing_other_matters",
        "material_weakness": "check_missing_material_weakness",
        "significant_deficiency": "check_missing_significant_deficiency",
        "other_findings": "check_missing_other_findings",
        "questioned_costs": "check_missing_questioned_costs",
        "repeat_prior_reference": "check_missing_repeat_prior_reference",
        "prior_references": "check_missing_prior_references",
        "is_valid": "check_missing_is_valid",
    },
    FORM_SECTIONS.ADDITIONAL_EINS: {
        "additional_ein": "check_eins_are_not_empty",
    },
    FORM_SECTIONS.ADDITIONAL_UEIS: {
        "additional_uei": "check_ueis_are_not_empty",
    },
    FORM_SECTIONS.NOTES_TO_SEFA: {
        "is_minimis_rate_used": "check_minimis_rate_used_is_not_blank",
        "rate_explained": "check_rate_explained_is_not_blank",
        "accounting_policies": "check_accounting_policies_is_not_blank",
        "note_title": "check_note_title_is_not_blank",
        "note_content": "check_note_content_is_not_blank",
        "contains_chart_or_table": "check_contains_chart_or_table_is_not_blank",
    },
    FORM_SECTIONS.SECONDARY_AUDITORS: {
        "secondary_auditor_name": "check_secondary_auditor_name_is_not_blank",
        "secondary_auditor_ein": "check_secondary_auditor_ein_is_not_blank",
        "secondary_auditor_address_street": "check_secondary_auditor_address_street_is_not_blank",
        "secondary_auditor_address_city": "check_secondary_auditor_address_city_is_not_blank",
        "secondary_auditor_address_state": "check_secondary_auditor_address_state_is_not_blank",
        "secondary_auditor_address_zipcode": "check_secondary_auditor_address_zipcode_is_not_blank",
        "secondary_auditor_contact_name": "check_secondary_auditor_contact_name_is_not_blank",
        "secondary_auditor_contact_title": "check_secondary_auditor_contact_title_is_not_blank",
        "secondary_auditor_contact_phone": "check_secondary_auditor_contact_phone_is_not_blank",
        "secondary_auditor_contact_email": "check_secondary_auditor_contact_email_is_not_blank",
    },
    FORM_SECTIONS.FINDINGS_TEXT: {
        "reference_number": "check_missing_reference_numbers",
        "text_of_finding": "check_missing_text_of_finding",
        "contains_chart_or_table": "check_contains_chart_or_table_is_not_blank",
    },
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: {
        "reference_number": "check_missing_reference_numbers",
        "planned_action": "check_missing_planned_action",
        "contains_chart_or_table": "check_contains_chart_or_table_is_not_blank",
    },
}


# check if any required field is missing
def has_all_required_fields(section_name):
    def _missing_required_fields(ir):
        required_field_ranges = map_required_field_ranges_to_workbook[section_name]
        errors = []
        for range_name, error_message_name in required_field_ranges.items():
            errors.extend(get_missing_value_errors(ir, range_name, error_message_name))

        if len(errors) > 0:
            logger.info("Raising a validation error.")
            raise ValidationError(errors)

    return _missing_required_fields
