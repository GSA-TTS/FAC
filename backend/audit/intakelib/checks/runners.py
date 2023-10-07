from django.core.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)

def run_general_checks(ir):
    errors = []
    for fun in federal_awards_checks:
        res = fun(ir)
        if res:
            errors.append(res)
    if len(errors) > 0:
        logger.info(f"Raising {len(errors)} IR validation error(s).")
        raise ValidationError(errors)


def run_all_federal_awards_checks(ir):
    errors = []
    for fun in federal_awards_checks:
        res = fun(ir)
        if isinstance(res, list):
            errors = errors + res
        elif res is None:
            pass
        else:
            errors.append(res)
    logger.info(f"Found {len(errors)} errors in the IR passes.")
    if len(errors) > 0:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)

from .check_uei_exists import uei_exists
general_checks = [
    uei_exists
]

from .check_state_cluster_names import state_cluster_names
from .check_other_cluster_names import other_cluster_names

federal_awards_checks = general_checks + [
    state_cluster_names,
    other_cluster_names
]
