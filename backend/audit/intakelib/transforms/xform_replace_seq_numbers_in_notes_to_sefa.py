import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name
    )

logger = logging.getLogger(__name__)

def replace_seq_numbers_in_notes_to_sefa(ir):
    seq = get_range_by_name(ir, "seq_number")
    logger.info(seq)
    new_values = list(map(lambda v: v + 1, range(len(seq["values"]))))
    new_ir = replace_range_by_name(ir, "seq_number", new_values)
    return new_ir
