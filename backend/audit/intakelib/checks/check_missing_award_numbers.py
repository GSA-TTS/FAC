import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


def missing_award_numbers(ir):
    ars = get_range_by_name(ir, "award_reference")
    errors = []
    for ndx, v in enumerate(ars["values"]):
        if v is None:
            errors.append(
                build_cell_error_tuple(
                    ir, ars, ndx, get_message("check_missing_award_numbers")
                )
            )

    return errors
