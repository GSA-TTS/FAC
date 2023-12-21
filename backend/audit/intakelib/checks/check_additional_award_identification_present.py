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
# Additional award identification should be present if the ALN three digit extension is RD#, or U##
def additional_award_identification(ir):
    extension = get_range_values_by_name(ir, "three_digit_extension")
    additional = get_range_values_by_name(ir, "additional_award_identification")
    errors = []
    patterns = [settings.REGEX_RD_EXTENSION, settings.REGEX_U_EXTENSION]
    for index, (ext, add) in enumerate(zip(extension, additional)):
        if any(re.match(pattern, ext) for pattern in patterns) and (
            (add is None) or (str(add).strip() == "")
        ):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    get_range_by_name(ir, "additional_award_identification"),
                    index,
                    get_message("check_additional_award_identification_present"),
                )
            )

    return errors
