from django.core.exceptions import ValidationError
import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


# FIXME: We need comments on all the validations?
def missing_award_numbers(ir):
    ars = get_range_by_name(ir, "award_reference")
    errors = []
    # FIXME: Get rid of all abbreviated variable names.
    for index, award_number in enumerate(ars["values"]):
        if award_number is None:
            errors.append(
                build_cell_error_tuple(
                    ir, ars, index, get_message("check_missing_award_numbers")
                )
            )
    if len(errors) > 0:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)
