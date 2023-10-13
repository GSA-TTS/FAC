import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
    remove_range_by_name,
    remove_null_rows
)
from pprint import pprint

logger = logging.getLogger(__name__)

def trim_null_from_content_fields_in_notes_to_sefa(ir):
    # First, get rid of the sequence number column.
    without_seq_ir = remove_range_by_name(ir, "seq_number")
    # Now, remove extra nulls from content columns
    for sheet in without_seq_ir:
        remove_null_rows(sheet)

    return without_seq_ir
