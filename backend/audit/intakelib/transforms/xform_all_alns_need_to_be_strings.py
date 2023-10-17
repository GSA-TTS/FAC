import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
)

logger = logging.getLogger(__name__)


def all_alns_need_to_be_strings(ir):
    agencies = get_range_by_name(ir, "federal_agency_prefix")
    new_values = list(map(lambda v: str(v), agencies["values"]))
    new_ir = replace_range_by_name(ir, "federal_agency_prefix", new_values)

    extensions = get_range_by_name(ir, "three_digit_extension")
    new_values = list(map(lambda v: str(v), extensions["values"]))
    new_ir = replace_range_by_name(ir, "three_digit_extension", new_values)

    return new_ir
