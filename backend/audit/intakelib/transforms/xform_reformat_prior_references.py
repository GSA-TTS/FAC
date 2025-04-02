import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
)
import re

logger = logging.getLogger(__name__)


# The prior references field might look like
# 2023-001
# or
# 2023-001,2022-006
# but people tend to like to insert spaces and other things.
#
# Because whitespace should never impact the meaning of this field, especially around the
# comma, we're going to strip whitespace from within the field.
#
# We do this by:
# 1. Stripping the string (removing leading and trailing whitespace)
# 2. Removing all whitespace internal to the string.
def reformat_prior_references(ir):
    references = get_range_by_name(ir, "prior_references")
    new_values = list(
        map(lambda v: re.sub(r"\s+", "", str(v).strip()), references["values"])
    )
    new_ir = replace_range_by_name(ir, "prior_references", new_values)
    return new_ir
