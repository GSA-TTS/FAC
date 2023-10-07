import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name
) 
from .util import (
    get_message,
    build_cell_error_tuple
    )

logger = logging.getLogger(__name__)

def loan_guarantee(ir):
    is_guaranteed = get_range_by_name(ir, "is_guaranteed")
    lbpe = get_range_by_name(ir, "loan_balance_at_audit_period_end")

    errors = []
    for ndx, (guarantee, balance) in enumerate(zip(is_guaranteed["values"],
                                      lbpe["values"])):
        if ((guarantee == 'N')
            and balance
            ):
            errors.append(build_cell_error_tuple(ir,
                                                lbpe,
                                                ndx,
                                                get_message("check_loan_guarantee_empty_when_n")
                                                ))
        elif ((guarantee == 'Y')
            and not balance
            ):
            errors.append(build_cell_error_tuple(ir,
                                                lbpe,
                                                ndx,
                                                get_message("check_loan_guarantee_present_when_y")
                                                ))

    return errors
