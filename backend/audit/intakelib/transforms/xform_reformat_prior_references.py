import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
)
import re

logger = logging.getLogger(__name__)


def reformat_prior_references(ir):
    references = get_range_by_name(ir, "prior_references")
    new_values = list(
        map(lambda v: re.sub(r"\s+,", ",", str(v).strip()), references["values"])
    )
    new_ir = replace_range_by_name(ir, "prior_references", new_values)
    return new_ir
