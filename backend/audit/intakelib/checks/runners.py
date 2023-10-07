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


from .check_uei_exists import uei_exists
from .check_is_a_workbook import is_a_workbook

general_checks = [is_a_workbook, uei_exists]

from .check_is_right_workbook import is_right_workbook
from .check_state_cluster_names import state_cluster_names
from .check_other_cluster_names import other_cluster_names
from .check_direct_award_is_not_blank import direct_award_is_not_blank
from .check_passthrough_name_when_no_direct import passthrough_name_when_no_direct
from .check_loan_guarantee import loan_guarantee

federal_awards_checks = general_checks + [
    is_right_workbook("FederalAwardsExpended"),
    state_cluster_names,
    other_cluster_names,
    direct_award_is_not_blank,
    passthrough_name_when_no_direct,
    loan_guarantee,
]

notes_to_sefa_checks = general_checks + [
    is_right_workbook("NotesToSefa"),
]
