from django.core.exceptions import ValidationError
import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


# FIXME: We need comments on all the validations?
def eins_are_not_empty(ir):
    addl_eins = get_range_by_name(ir, "additional_ein")
    errors = []
    for index, ein in enumerate(addl_eins["values"]):
        if ein is None:
            errors.append(
                build_cell_error_tuple(
                    ir, addl_eins, index, get_message("check_eins_are_not_empty")
                )
            )
    if len(errors) > 0:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)
