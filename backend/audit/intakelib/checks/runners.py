from django.core.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)


def run_all_federal_awards_checks(ir):
    errors = []
    for fun in federal_awards_checks:
        res = fun(ir)
        if res:
            errors.append(res)
    
    logger.info("Errors:", errors)
    if len(errors) > 0:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)


from .check_uei_exists import uei_exists
federal_awards_checks = [
    uei_exists    
]
