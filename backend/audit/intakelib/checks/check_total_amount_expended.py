import logging
from audit.intakelib.intermediate_representation import (
    get_range_values_by_name,
    get_range_by_name,
)
from audit.intakelib.common import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


# DESCRIPTION
# The sum of the amount_expended should equal the total_amount_expended
# B5=SUM(Form!F$2:F$MAX_ROWS)
def total_amount_expended_is_correct(ir):
    total_amount_expended_value = get_range_values_by_name(ir, "total_amount_expended")
    amount_expended_values = get_range_values_by_name(ir, "amount_expended")

    errors = []

    # Validating total_amount_expended
    computed_sum = sum(amount_expended_values)
    if computed_sum != total_amount_expended_value[0]:
        errors.append(
            build_cell_error_tuple(
                ir,
                get_range_by_name(ir, "total_amount_expended"),
                0,
                get_message("check_total_amount_expended").format(
                    total_amount_expended_value[0], computed_sum
                ),
            )
        )

    return errors
