import logging
from audit.intakelib.intermediate_representation import (
    get_range_values_by_name,
    get_range_by_name,
)
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


# DESCRIPTION
# Users sometimes leave this column blank.
# It must always be present.
def direct_award_is_not_blank(ir):
    is_direct = get_range_values_by_name(ir, "is_direct")
    errors = []
    for index, y_or_n in enumerate(is_direct):
        if (y_or_n is None) or (str(y_or_n).strip() == ""):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    get_range_by_name(ir, "is_direct"),
                    index,
                    get_message("check_direct_award_is_not_blank"),
                )
            )

    return errors
