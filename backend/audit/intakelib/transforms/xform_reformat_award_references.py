import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
)

logger = logging.getLogger(__name__)


# Tested by has_lowercase_award_reference.xlsx
def reformat_award_reference(ir):
    references = get_range_by_name(ir, "award_reference")
    new_values = list(map(lambda v: v.upper() if v else v, references["values"]))
    new_ir = replace_range_by_name(ir, "award_reference", new_values)
    return new_ir
