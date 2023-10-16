import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
)

logger = logging.getLogger(__name__)


def eins_need_to_be_strings(ir):
    eins = get_range_by_name(ir, "additional_ein")
    new_values = list(map(lambda v: str(v), eins["values"]))
    new_ir = replace_range_by_name(ir, "additional_ein", new_values)
    return new_ir
