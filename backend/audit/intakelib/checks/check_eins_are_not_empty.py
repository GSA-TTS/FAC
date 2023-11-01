from django.core.exceptions import ValidationError
import logging
from .util import get_missing_value_errors

logger = logging.getLogger(__name__)


# FIXME: We need comments on all the validations?
def eins_are_not_empty(ir):
    errors = get_missing_value_errors(ir, "additional_ein", "check_eins_are_not_empty")
    if len(errors) > 0:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)
