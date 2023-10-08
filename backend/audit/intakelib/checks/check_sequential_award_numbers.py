import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from .util import get_message, build_cell_error_tuple
import re

logger = logging.getLogger(__name__)


def sequential_award_numbers(ir):
    ars = get_range_by_name(ir, "award_reference")
    errors = []
    found = []
    for ndx, v in enumerate(ars["values"], 1):
        if not re.match("AWARD-[0-9]{4}", v):
            errors.append(
                build_cell_error_tuple(
                    ir, ars, ndx, get_message("check_sequential_award_numbers_regex")
                )
            )

        number_part = int(v.split("-")[1])
        if number_part != ndx:
            errors.append(
                build_cell_error_tuple(
                    ir, ars, ndx, 
                    get_message("check_sequential_award_numbers_off").format(v, f"AWARD-{ndx:04}")
                )
            )

    return errors
