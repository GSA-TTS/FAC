import logging
from audit.intakelib.intermediate_representation import (
    get_range_values_by_name,
    get_range_by_name,
)
from audit.intakelib.common import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


# DESCRIPTION
# The sum of the amount_expended for a given cfda_key should equal the corresponding federal_program_total
# J{0}=SUMIFS(amount_expended,cfda_key,V{0}))
def federal_program_total_is_correct(ir):
    federal_program_total = get_range_values_by_name(ir, "federal_program_total")
    cfda_key = get_range_values_by_name(ir, "cfda_key")
    amount_expended = get_range_values_by_name(ir, "amount_expended")

    errors = []

    # Validating each federal_program_total
    for idx, key in enumerate(cfda_key):
        # Compute the sum for current cfda_key
        computed_sum = sum(
            [amount for k, amount in zip(cfda_key, amount_expended) if k == key]
        )
        if computed_sum != federal_program_total[idx]:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    get_range_by_name(ir, "federal_program_total"),
                    idx,
                    get_message("check_federal_program_total").format(
                        federal_program_total[idx], computed_sum
                    ),
                )
            )

    return errors
