import logging
from django.conf import settings
from audit.intakelib.intermediate_representation import (
    get_range_values_by_name,
    get_range_by_name,
)
from audit.intakelib.common import get_message, build_cell_error_tuple
from ..common.util import is_int

logger = logging.getLogger(__name__)


# DESCRIPTION
# If the loan is not a guarantee, AND there is a balance, that is a problem and the application throws an error.
# If the loan is is a guarantee, there should be a balance.
# WHY
# A guarantee means we want to know how much was guaranteed.
def loan_balance_present(ir):
    is_guaranteed = get_range_values_by_name(ir, "is_guaranteed")
    loan_balance_at_period_end = get_range_values_by_name(
        ir, "loan_balance_at_audit_period_end"
    )

    errors = []
    for index, (guarantee, balance) in enumerate(
        zip(is_guaranteed, loan_balance_at_period_end)
    ):
        if (guarantee == "N") and balance:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    get_range_by_name(ir, "loan_balance_at_audit_period_end"),
                    index,
                    get_message("check_loan_guarantee_empty_when_n"),
                )
            )
        elif (guarantee == "Y") and not (
            balance in [settings.NOT_APPLICABLE, settings.GSA_MIGRATION]
            or is_int(balance)
        ):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    get_range_by_name(ir, "loan_balance_at_audit_period_end"),
                    index,
                    get_message("check_loan_guarantee_present_when_y"),
                )
            )

    return errors
