import logging
from audit.intakelib.intermediate_representation import get_range_values_by_name
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)

# DESCRIPTION
# This must always be present.
def federal_award_passed_always_present(ir):
    is_passed = get_range_values_by_name(ir, "is_passed")
    errors = []
    for index, y_or_n in enumerate(is_passed):
        if (y_or_n is None) or (str(y_or_n).strip() == ""):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    is_passed,
                    index,
                    get_message("check_federal_award_passed_always_present"),
                )
            )

    return errors
