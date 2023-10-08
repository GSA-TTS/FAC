from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


def run_general_checks(ir):
    errors = []
    for fun in federal_awards_checks:
        res = fun(ir)
        if res:
            errors.append(res)
    if len(errors) > 0:
        logger.info(f"Raising {len(errors)} IR validation error(s).")
        raise ValidationError(errors)


def run_all_checks(ir, list_of_checks):
    errors = []
    for fun in list_of_checks:
        res = fun(ir)
        if isinstance(res, list):
            errors = errors + res
        elif res is None:
            pass
        else:
            errors.append(res)
    logger.info(f"Found {len(errors)} errors in the IR passes.")
    if len(errors) > 0:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)


def run_all_federal_awards_checks(ir):
    run_all_checks(ir, federal_awards_checks)


def run_all_notes_to_sefa_checks(ir):
    run_all_checks(ir, notes_to_sefa_checks)

def run_all_audit_finding_checks(ir):
    run_all_checks(ir, audit_findings_checks)

from .check_uei_exists import uei_exists
from .check_is_a_workbook import is_a_workbook
from .check_look_for_empty_rows import look_for_empty_rows

general_checks = [is_a_workbook, uei_exists, look_for_empty_rows]

from .check_is_right_workbook import is_right_workbook
from .check_state_cluster_names import state_cluster_names
from .check_other_cluster_names import other_cluster_names
from .check_direct_award_is_not_blank import direct_award_is_not_blank
from .check_passthrough_name_when_no_direct import passthrough_name_when_no_direct
from .check_loan_guarantee import loan_guarantee
from .check_no_major_program_no_type import no_major_program_no_type
from .check_no_repeat_findings import no_repeat_findings
from .check_missing_award_numbers import missing_award_numbers
from .check_all_unique_award_numbers import all_unique_award_numbers
from .check_sequential_award_numbers import sequential_award_numbers
from .check_num_findings_always_present import num_findings_always_present
from .check_cluster_name_always_present import cluster_name_always_present

federal_awards_checks = general_checks + [
    is_right_workbook("FederalAwardsExpended"),
    missing_award_numbers,
    num_findings_always_present,
    cluster_name_always_present,
    state_cluster_names,
    other_cluster_names,
    direct_award_is_not_blank,
    passthrough_name_when_no_direct,
    loan_guarantee,
    no_major_program_no_type,
    all_unique_award_numbers,
    sequential_award_numbers
]

notes_to_sefa_checks = general_checks + [
    is_right_workbook("NotesToSefa"),
]

audit_findings_checks = general_checks + [
    is_right_workbook("FindingsUniformGuidance"),
    no_repeat_findings
]
