import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


def passthrough_name_when_no_direct(ir):
    is_direct = get_range_by_name(ir, "is_direct")
    passthrough_name = get_range_by_name(ir, "passthrough_name")

    errors = []
    for ndx, (v, pn) in enumerate(zip(is_direct["values"], passthrough_name["values"])):
        if (v == "N") and (pn is None):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    is_direct,
                    ndx,
                    get_message("check_passthrough_name_when_no_direct"),
                )
            )

    return errors
