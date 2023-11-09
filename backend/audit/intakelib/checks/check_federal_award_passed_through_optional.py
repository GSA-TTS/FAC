import logging
from audit.intakelib.intermediate_representation import (
    get_range_values_by_name,
    get_range_by_name,
)
from audit.intakelib.common import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


# DESCRIPTION
# Amount passed through must be present if "Y" is selected for "Federal Award Passed Through"
def federal_award_amount_passed_through_optional(ir):
    is_passed_values = get_range_values_by_name(ir, "is_passed")
    subrecipient_amount_values = get_range_values_by_name(ir, "subrecipient_amount")
    errors = []

    for index, (is_passed, subrecipient_amount) in enumerate(
        zip(is_passed_values, subrecipient_amount_values)
    ):
        if is_passed == "Y" and subrecipient_amount is None:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    get_range_by_name(ir, "subrecipient_amount"),
                    index,
                    get_message("check_federal_award_amount_passed_through_required"),
                )
            )
        elif is_passed == "N" and subrecipient_amount is not None:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    get_range_by_name(ir, "subrecipient_amount"),
                    index,
                    get_message(
                        "check_federal_award_amount_passed_through_not_allowed"
                    ),
                )
            )

    return errors
