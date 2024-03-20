import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from audit.intakelib.common import get_message, build_cell_error_tuple
import re

logger = logging.getLogger(__name__)

AWARD_REFERENCES_REGEX = r"^AWARD-(?!0{4,5}$)[0-9]{4,5}$"


def sequential_award_numbers(ir):
    ars = get_range_by_name(ir, "award_reference")
    errors = []
    for ndx, v in enumerate(ars["values"], 1):
        # Might have an award of length 4 or 5.
        number_part_str = v.split("-")[1]
        number_part_int = int(v.split("-")[1])
        length_of_ref = len(number_part_str)
        if length_of_ref == 4:
            msg = f"AWARD-{ndx:04}"
        else:
            msg = f"AWARD-{ndx:05}"

        if not re.match(AWARD_REFERENCES_REGEX, str(v)):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    ars,
                    ndx,
                    get_message("check_sequential_award_numbers_regex").format(msg),
                )
            )

        if number_part_int != ndx:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    ars,
                    ndx,
                    get_message("check_sequential_award_numbers_off").format(v, msg),
                )
            )

    return errors
