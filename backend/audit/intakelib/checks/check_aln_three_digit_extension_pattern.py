import logging
import re

from django.conf import settings
from audit.intakelib.intermediate_representation import (
    get_range_values_by_name,
    get_range_by_name,
)
from audit.intakelib.common import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


# DESCRIPTION
# The three digit extension should follow one of these formats: ###, RD#, or U##, where # represents a number
# TESTED BY
# has_bad_alns.xlsx
def aln_three_digit_extension(ir):
    extension = get_range_values_by_name(ir, "three_digit_extension")
    errors = []
    # Define regex patterns
    patterns = [
        settings.REGEX_RD_EXTENSION,
        settings.REGEX_THREE_DIGIT_EXTENSION,
        settings.REGEX_U_EXTENSION,
        rf"^{re.escape(settings.GSA_MIGRATION)}$",
    ]
    for index, ext in enumerate(extension):
        # Check if ext does not match any of the regex patterns
        if not any(re.match(pattern, str(ext)) for pattern in patterns):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    get_range_by_name(ir, "three_digit_extension"),
                    index,
                    get_message("check_aln_three_digit_extension_invalid"),
                )
            )

    return errors
