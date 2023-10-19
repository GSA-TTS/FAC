from django.core.exceptions import ValidationError
import logging
from audit.fixtures.excel import FORM_SECTIONS

############
# General checks
from .check_uei_exists import uei_exists
from .check_is_a_workbook import is_a_workbook
from .check_look_for_empty_rows import look_for_empty_rows
from .check_start_and_end_rows_of_all_columns_are_same import (
    start_and_end_rows_of_all_columns_are_same,
)

############
# Federal awards checks
from .check_is_right_workbook import is_right_workbook
from .check_state_cluster_names import state_cluster_names
from .check_other_cluster_names import other_cluster_names
from .check_direct_award_is_not_blank import direct_award_is_not_blank
from .check_passthrough_name_when_no_direct import passthrough_name_when_no_direct
from .check_loan_guarantee import loan_guarantee
from .check_loan_balance import loan_balance
from .check_no_major_program_no_type import no_major_program_no_type
from .check_missing_award_numbers import missing_award_numbers
from .check_all_unique_award_numbers import all_unique_award_numbers
from .check_sequential_award_numbers import sequential_award_numbers
from .check_num_findings_always_present import num_findings_always_present
from .check_cluster_name_always_present import cluster_name_always_present
from .check_federal_award_passed_always_present import (
    federal_award_passed_always_present,
)
from .check_cardinality_of_passthrough_names_and_ids import (
    cardinality_of_passthrough_names_and_ids,
)

############
# Audit findings checks
from .check_no_repeat_findings import no_repeat_findings
from .check_findings_grid_validation import findings_grid_validation

logger = logging.getLogger(__name__)

general_checks = [
    is_a_workbook,
    uei_exists,
    look_for_empty_rows,
    start_and_end_rows_of_all_columns_are_same,
]

federal_awards_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED),
    missing_award_numbers,
    num_findings_always_present,
    cluster_name_always_present,
    federal_award_passed_always_present,
    state_cluster_names,
    other_cluster_names,
    direct_award_is_not_blank,
    passthrough_name_when_no_direct,
    loan_balance,
    loan_guarantee,
    no_major_program_no_type,
    all_unique_award_numbers,
    sequential_award_numbers,
    cardinality_of_passthrough_names_and_ids,
]

notes_to_sefa_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.NOTES_TO_SEFA),
]

audit_findings_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE),
    no_repeat_findings,
    findings_grid_validation,
]

additional_eins_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.ADDITIONAL_EINS),
]

additional_ueis_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.ADDITIONAL_UEIS),
]

audit_findings_text_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.FINDINGS_TEXT),
]

corrective_action_plan_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.CORRECTIVE_ACTION_PLAN),
]

secondary_auditors_checks = general_checks + [
    is_right_workbook(FORM_SECTIONS.SECONDARY_AUDITORS),
]


def run_all_checks(ir, list_of_checks, section_name=None):
    errors = []
    if section_name:
        res = is_right_workbook(section_name)(ir)
        if res:
            errors.append(res)
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


def run_all_general_checks(ir, section_name):
    run_all_checks(ir, general_checks, section_name)


def run_all_federal_awards_checks(ir):
    run_all_checks(ir, federal_awards_checks)


def run_all_notes_to_sefa_checks(ir):
    run_all_checks(ir, notes_to_sefa_checks)


def run_all_audit_finding_checks(ir):
    run_all_checks(ir, audit_findings_checks)


def run_all_additional_eins_checks(ir):
    run_all_checks(ir, additional_eins_checks)


def run_all_additional_ueis_checks(ir):
    run_all_checks(ir, additional_ueis_checks)


def run_all_audit_findings_text_checks(ir):
    run_all_checks(ir, audit_findings_text_checks)


def run_all_corrective_action_plan_checks(ir):
    run_all_checks(ir, corrective_action_plan_checks)


def run_all_secondary_auditors_checks(ir):
    run_all_checks(ir, secondary_auditors_checks)
