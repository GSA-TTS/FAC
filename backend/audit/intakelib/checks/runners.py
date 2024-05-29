from django.core.exceptions import ValidationError
import logging

from census_historical_migration.invalid_record import InvalidRecord

from .check_finding_award_references_pattern import award_references_pattern
from .check_cluster_names import check_cluster_names
from audit.fixtures.excel import FORM_SECTIONS
from .check_gsa_migration_keyword import check_for_gsa_migration_keyword
from .check_data_row_range_in_form_sheet import validate_ranges

############
# General checks
from .check_uei_schema import verify_auditee_uei_schema
from .check_uei_match import verify_auditee_uei_match
from .check_uei_exists import uei_exists
from .check_is_a_workbook import is_a_workbook
from .check_look_for_empty_rows import look_for_empty_rows
from .check_start_and_end_rows_of_all_columns_are_same import (
    start_and_end_rows_of_all_columns_are_same,
)
from .check_version_number import validate_workbook_version

############
# Federal awards checks
from .check_is_right_workbook import is_right_workbook
from .check_state_cluster_names import state_cluster_names
from .check_other_cluster_names import other_cluster_names
from .check_passthrough_name_when_no_direct import passthrough_name_when_no_direct
from .check_loan_balance_present import loan_balance_present
from .check_loan_balance_entries import loan_balance_entry_is_valid
from .check_no_major_program_no_type import no_major_program_no_type
from .check_all_unique_award_numbers import all_unique_award_numbers
from .check_sequential_award_numbers import sequential_award_numbers
from .check_aln_three_digit_extension_pattern import aln_three_digit_extension
from .check_additional_award_identification_present import (
    additional_award_identification,
)
from .check_federal_program_total import federal_program_total_is_correct
from .check_cluster_total import cluster_total_is_correct
from .check_total_amount_expended import total_amount_expended_is_correct
from .check_federal_award_passed_through_optional import (
    federal_award_amount_passed_through_optional,
)
from .check_cardinality_of_passthrough_names_and_ids import (
    cardinality_of_passthrough_names_and_ids,
)
from .check_has_all_the_named_ranges import has_all_the_named_ranges
from .check_missing_required_fields import has_all_required_fields
from .check_y_or_n__fields import has_invalid_yorn_field

############
# Audit findings checks
from .check_no_repeat_findings import no_repeat_findings
from .check_findings_grid_validation import findings_grid_validation
from .check_finding_prior_references_pattern import prior_references_pattern
from .check_finding_reference_pattern import finding_reference_pattern
from .check_aln_prefix_pattern import aln_agency_prefix

logger = logging.getLogger(__name__)

general_checks = [
    is_a_workbook,
    validate_workbook_version,
    uei_exists,
    verify_auditee_uei_schema,
    verify_auditee_uei_match,
    look_for_empty_rows,
    start_and_end_rows_of_all_columns_are_same,
    validate_ranges,
]

federal_awards_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED),
    has_all_the_named_ranges(FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED),
    has_all_required_fields(FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED),
    has_invalid_yorn_field(FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED),
    award_references_pattern,
    federal_award_amount_passed_through_optional,
    check_cluster_names,
    state_cluster_names,
    other_cluster_names,
    passthrough_name_when_no_direct,
    loan_balance_present,
    loan_balance_entry_is_valid,
    no_major_program_no_type,
    all_unique_award_numbers,
    sequential_award_numbers,
    aln_agency_prefix,
    aln_three_digit_extension,
    additional_award_identification,
    federal_program_total_is_correct,
    cluster_total_is_correct,
    total_amount_expended_is_correct,
    cardinality_of_passthrough_names_and_ids,
]

notes_to_sefa_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.NOTES_TO_SEFA),
    has_all_the_named_ranges(FORM_SECTIONS.NOTES_TO_SEFA),
    has_all_required_fields(FORM_SECTIONS.NOTES_TO_SEFA),
    has_invalid_yorn_field(FORM_SECTIONS.NOTES_TO_SEFA),
]

audit_findings_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE),
    has_all_the_named_ranges(FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE),
    has_all_required_fields(FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE),
    has_invalid_yorn_field(FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE),
    award_references_pattern,
    prior_references_pattern,
    finding_reference_pattern,
    no_repeat_findings,
    findings_grid_validation,
]

additional_eins_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.ADDITIONAL_EINS),
    has_all_the_named_ranges(FORM_SECTIONS.ADDITIONAL_EINS),
    has_all_required_fields(FORM_SECTIONS.ADDITIONAL_EINS),
]

additional_ueis_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.ADDITIONAL_UEIS),
    has_all_the_named_ranges(FORM_SECTIONS.ADDITIONAL_UEIS),
    has_all_required_fields(FORM_SECTIONS.ADDITIONAL_UEIS),
]

audit_findings_text_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.FINDINGS_TEXT),
    has_all_the_named_ranges(FORM_SECTIONS.FINDINGS_TEXT),
    has_all_required_fields(FORM_SECTIONS.FINDINGS_TEXT),
    has_invalid_yorn_field(FORM_SECTIONS.FINDINGS_TEXT),
    finding_reference_pattern,
]

corrective_action_plan_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.CORRECTIVE_ACTION_PLAN),
    has_all_the_named_ranges(FORM_SECTIONS.CORRECTIVE_ACTION_PLAN),
    has_all_required_fields(FORM_SECTIONS.CORRECTIVE_ACTION_PLAN),
    has_invalid_yorn_field(FORM_SECTIONS.CORRECTIVE_ACTION_PLAN),
    finding_reference_pattern,
]

secondary_auditors_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.SECONDARY_AUDITORS),
    has_all_the_named_ranges(FORM_SECTIONS.SECONDARY_AUDITORS),
    has_all_required_fields(FORM_SECTIONS.SECONDARY_AUDITORS),
]

skippable_checks = {
    "federal_program_total_is_correct": federal_program_total_is_correct
}


def run_all_checks(
    ir, list_of_checks, section_name=None, is_data_migration=False, auditee_uei=None
):
    """Run all the checks in the list_of_checks on the IR.
    If a section_name is provided, run the section check as well.
    If this is a data migration, then there are some checks we do not want to run.
    If this is not a data migration, then we want to make sure no one put in a GSA_MIGRATION keyword.
    """
    errors = []

    errors += run_section_check(ir, section_name)
    list_of_checks = filter_checks_for_data_migration(list_of_checks, is_data_migration)
    check_for_gsa_migration_keyword_if_needed(ir, is_data_migration)

    for fun in list_of_checks:
        res = run_check(fun, ir, is_data_migration, auditee_uei)
        errors += process_check_result(res)

    log_errors(errors)
    if errors:
        raise ValidationError(errors)


def run_section_check(ir, section_name):
    """Run the section check if it is provided."""
    if section_name:
        res = is_right_workbook(section_name)(ir)
        if res:
            return [res]
    return []


def filter_checks_for_data_migration(list_of_checks, is_data_migration):
    """If this is a data migration, then there are some checks we do not want to run."""
    if is_data_migration and list_of_checks == federal_awards_checks:
        return list(filter(lambda f: f != check_cluster_names, list_of_checks))
    return list_of_checks


def check_for_gsa_migration_keyword_if_needed(ir, is_data_migration):
    """If this is not a data migration, then we want to make sure no one put in a GSA_MIGRATION keyword."""
    if not is_data_migration:
        check_for_gsa_migration_keyword(ir)


def get_key_by_value(d, target_value):
    keys = [key for key, value in d.items() if value == target_value]
    return keys[0] if keys else None


def run_check(fun, ir, is_data_migration, auditee_uei):
    """Run the validation check if it is not skippable, or if it is skippable, only run if this is not a data migration."""
    fun_name = get_key_by_value(skippable_checks, fun)
    if (
        is_data_migration
        and fun_name
        and fun_name in InvalidRecord.fields["validations_to_skip"]
    ):
        return None
    elif fun == verify_auditee_uei_schema:
        return fun(ir, auditee_uei)
    else:
        return fun(ir)


def process_check_result(res):
    """Process the result of a validation check and return a list of errors."""
    if isinstance(res, list) and all(map(lambda v: isinstance(v, tuple), res)):
        return res
    elif isinstance(res, tuple):
        return [res]
    return []


def log_errors(errors):
    """Log the number of errors found in the IR passes."""
    logger.info(f"Found {len(errors)} errors in the IR passes.")
    if errors:
        logger.info("Raising a validation error.")


def run_all_general_checks(ir, section_name, is_data_migration=False, auditee_uei=None):
    run_all_checks(
        ir,
        general_checks,
        section_name,
        is_data_migration=is_data_migration,
        auditee_uei=auditee_uei,
    )


def run_all_federal_awards_checks(ir, is_data_migration=False):
    run_all_checks(ir, federal_awards_checks, is_data_migration=is_data_migration)


def run_all_notes_to_sefa_checks(ir, is_data_migration=False):
    run_all_checks(ir, notes_to_sefa_checks, is_data_migration=is_data_migration)


def run_all_audit_finding_checks(ir, is_data_migration=False):
    run_all_checks(ir, audit_findings_checks, is_data_migration=is_data_migration)


def run_all_additional_eins_checks(ir, is_data_migration=False):
    run_all_checks(ir, additional_eins_checks, is_data_migration=is_data_migration)


def run_all_additional_ueis_checks(ir, is_data_migration=False):
    run_all_checks(ir, additional_ueis_checks, is_data_migration=is_data_migration)


def run_all_audit_findings_text_checks(ir, is_data_migration=False):
    run_all_checks(ir, audit_findings_text_checks, is_data_migration=is_data_migration)


def run_all_corrective_action_plan_checks(ir, is_data_migration=False):
    run_all_checks(
        ir, corrective_action_plan_checks, is_data_migration=is_data_migration
    )


def run_all_secondary_auditors_checks(ir, is_data_migration=False):
    run_all_checks(ir, secondary_auditors_checks, is_data_migration=is_data_migration)
