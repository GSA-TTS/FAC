import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
)

logger = logging.getLogger(__name__)


def all_passthrough_id_need_to_be_strings(ir):
    passthrough_ids = get_range_by_name(ir, "passthrough_identifying_number")
    new_values = [str(v) if v is not None else None for v in passthrough_ids["values"]]
    new_ir = replace_range_by_name(ir, "passthrough_identifying_number", new_values)

    return new_ir
