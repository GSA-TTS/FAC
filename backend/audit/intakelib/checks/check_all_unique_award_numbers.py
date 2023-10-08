import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


def all_unique_award_numbers(ir):
    ars = get_range_by_name(ir, "award_reference")
    errors = []
    found = []
    for ndx, v in enumerate(ars["values"]):
        if v in found:
            errors.append(
                build_cell_error_tuple(
                    ir, ars, ndx, get_message("check_all_unique_award_numbers")
                )
            )
        if v not in found:
            found.append(v)

    return errors
