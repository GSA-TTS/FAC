from django.core.exceptions import ValidationError
import logging
from .util import get_missing_value_errors

logger = logging.getLogger(__name__)


# FIXME: We need comments on all the validations?
def missing_award_numbers(ir):
    errors = get_missing_value_errors(
        ir, "award_reference", "check_missing_award_numbers"
    )

    if len(errors) > 0:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)
