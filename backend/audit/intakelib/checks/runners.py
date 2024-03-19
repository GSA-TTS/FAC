from django.core.exceptions import ValidationError
import logging

from .check_finding_award_references_pattern import award_references_pattern
from .check_cluster_names import check_cluster_names
from audit.fixtures.excel import FORM_SECTIONS
from .check_gsa_migration_keyword import check_for_gsa_migration_keyword


############
# General checks
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
    look_for_empty_rows,
    start_and_end_rows_of_all_columns_are_same,
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
]

corrective_action_plan_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.CORRECTIVE_ACTION_PLAN),
    has_all_the_named_ranges(FORM_SECTIONS.CORRECTIVE_ACTION_PLAN),
    has_all_required_fields(FORM_SECTIONS.CORRECTIVE_ACTION_PLAN),
    has_invalid_yorn_field(FORM_SECTIONS.CORRECTIVE_ACTION_PLAN),
]

secondary_auditors_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.SECONDARY_AUDITORS),
    has_all_the_named_ranges(FORM_SECTIONS.SECONDARY_AUDITORS),
    has_all_required_fields(FORM_SECTIONS.SECONDARY_AUDITORS),
]


def run_all_checks(ir, list_of_checks, section_name=None, is_data_migration=False):
    errors = []
    if section_name:
        res = is_right_workbook(section_name)(ir)
        if res:
            errors.append(res)

    # If this is a data migration, then there are some checks we do not want to run.
    #
    if is_data_migration:
        if list_of_checks == federal_awards_checks:
            list_of_checks = list(
                filter(lambda f: f != check_cluster_names, list_of_checks)
            )
    else:
        # This is not a data migration.
        # We want to make sure no one put in a GSA_MIGRATION keyword.
        check_for_gsa_migration_keyword(ir)

    for fun in list_of_checks:
        res = fun(ir)
        if isinstance(res, list) and all(map(lambda v: isinstance(v, tuple), res)):
            errors = errors + res
        elif isinstance(res, tuple):
            errors.append(res)
        else:
            pass
    logger.info(f"Found {len(errors)} errors in the IR passes.")
    if len(errors) > 0:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)


def run_all_general_checks(ir, section_name, is_data_migration=False):
    run_all_checks(
        ir, general_checks, section_name, is_data_migration=is_data_migration
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
