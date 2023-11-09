import logging
from audit.intakelib.intermediate_representation import (
    get_range_values_by_name,
    get_range_by_name,
)
from audit.intakelib.common import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


# DESCRIPTION
# This makes sure that the loan guarantee is either a numerical value or N/A or an empty string.
def loan_balance_entry_is_valid(ir):
    loan_balance_at_period_end = get_range_values_by_name(
        ir, "loan_balance_at_audit_period_end"
    )

    errors = []
    for index, balance in enumerate(loan_balance_at_period_end):
        # Check if balance is not a number, empty string, or "N/A"
        if not (balance in ["N/A", "", None] or _is_int(balance)):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    get_range_by_name(ir, "loan_balance_at_audit_period_end"),
                    index,
                    get_message("check_loan_balance").format(balance),
                )
            )

    return errors


# check if the given string can be converted to an int
def _is_int(s):
    try:
        value = int(s)
        return value >= 0
    except ValueError:
        return False
