import logging
from .util import get_missing_value_errors

logger = logging.getLogger(__name__)


# DESCRIPTION
# This must always be present.
def federal_award_passed_always_present(ir):
    return get_missing_value_errors(
        ir, "is_passed", "check_federal_award_passed_always_present"
    )
