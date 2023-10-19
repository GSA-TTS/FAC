import logging
import re
from audit.intakelib.intermediate_representation import (
    get_range_values_by_name,
    get_range_by_name,
)
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)

REGEX_RD_EXTENSION = r"^RD[0-9]?$"
REGEX_THREE_DIGIT_EXTENSION = r"^[0-9]{3}[A-Za-z]{0,1}$"
REGEX_U_EXTENSION = r"^U[0-9]{2}$"


# DESCRIPTION
# The three digit extension should follow one of these formats: ###, RD#, or U##, where # represents a number
def aln_three_digit_extension(ir):
    extension = get_range_values_by_name(ir, "three_digit_extension")
    errors = []
    # Define regex patterns
    patterns = [REGEX_RD_EXTENSION, REGEX_THREE_DIGIT_EXTENSION, REGEX_U_EXTENSION]
    for index, ext in enumerate(extension):
        # Check if ext is None or does not match any of the regex patterns
        if not ext:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    get_range_by_name(ir, "three_digit_extension"),
                    index,
                    get_message("check_aln_three_digit_extension_missing"),
                )
            )
        elif not any(re.match(pattern, ext) for pattern in patterns):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    get_range_by_name(ir, "three_digit_extension"),
                    index,
                    get_message("check_aln_three_digit_extension_invalid"),
                )
            )

    return errors
