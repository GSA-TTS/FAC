import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    insert_new_range,
)

logger = logging.getLogger(__name__)

def insert_sequence_nums_into_notes_to_sefa(ir):
    contains_range = get_range_by_name(ir, "contains_chart_or_table")
    new_values = list(map(lambda v: v + 1, range(len(contains_range["values"]))))
    new_ir = insert_new_range(ir, "AdditionalNotes", "seq_number", "D", 2, new_values)
    return new_ir
