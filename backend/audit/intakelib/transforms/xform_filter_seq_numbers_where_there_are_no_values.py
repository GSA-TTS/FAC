import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
    appears_empty,
)

logger = logging.getLogger(__name__)


def filter_seq_numbers_where_there_are_no_values(ir):
    contains_chart = get_range_by_name(ir, "contains_chart_or_table")
    note_content = get_range_by_name(ir, "note_content")
    note_title = get_range_by_name(ir, "note_title")
    seq_numbers = get_range_by_name(ir, "seq_number")
    new_seq_numbers = []
    for indx, (contains_ch, note_con, note_tit, seq_num) in enumerate(
        zip(
            contains_chart["values"],
            note_content["values"],
            note_title["values"],
            seq_numbers["values"],
        )
    ):
        # We only want seq numbers where there are values in the other columns
        if (
            appears_empty(note_con)
            and appears_empty(contains_ch)
            and appears_empty(note_tit)
        ):
            pass
        else:
            new_seq_numbers.append(seq_num)

    new_ir = replace_range_by_name(ir, "seq_number", new_seq_numbers)
    return new_ir
