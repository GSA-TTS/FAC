import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


def direct_award_is_not_blank(ir):
    is_direct = get_range_by_name(ir, "is_direct")
    errors = []
    for ndx, v in zip(range(len(is_direct)), is_direct["values"]):
        if v is None:
            errors.append(
                build_cell_error_tuple(
                    ir, is_direct, ndx, get_message("check_direct_award_is_not_blank")
                )
            )

    return errors
