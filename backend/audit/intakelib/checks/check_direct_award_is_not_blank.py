import logging
from .util import get_missing_value_errors

logger = logging.getLogger(__name__)


# DESCRIPTION
# Users sometimes leave this column blank.
# It must always be present.
def direct_award_is_not_blank(ir):
    return get_missing_value_errors(ir, "is_direct", "check_direct_award_is_not_blank")
