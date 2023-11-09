import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from audit.intakelib.common import (
    get_message,
    build_cell_error_tuple,
    is_value_marked_na,
)

logger = logging.getLogger(__name__)


def no_repeat_findings(ir):
    repeat_prior_reference = get_range_by_name(ir, "repeat_prior_reference")
    prior_references = get_range_by_name(ir, "prior_references")

    errors = []
    for ndx, (is_rep, prior) in enumerate(
        zip(repeat_prior_reference["values"], prior_references["values"])
    ):
        if (is_rep == "N") and (not is_value_marked_na(prior)):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    prior_references,
                    ndx,
                    get_message("check_no_repeat_findings_when_n"),
                )
            )
        elif (is_rep == "Y") and ((not prior) or (is_value_marked_na(prior))):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    prior_references,
                    ndx,
                    get_message("check_no_repeat_findings_when_y"),
                )
            )

    return errors
