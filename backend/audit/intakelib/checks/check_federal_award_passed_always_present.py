import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


def federal_award_passed_always_present(ir):
    is_passed = get_range_by_name(ir, "is_passed")
    errors = []
    for ndx, v in enumerate(is_passed["values"]):
        if (v is None) or (str(v).strip() == ""):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    is_passed,
                    ndx,
                    get_message("check_federal_award_passed_always_present"),
                )
            )

    return errors
