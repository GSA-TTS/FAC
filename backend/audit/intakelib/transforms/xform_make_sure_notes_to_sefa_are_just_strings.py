import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
)

logger = logging.getLogger(__name__)


def make_sure_notes_to_sefa_are_just_strings(ir):
    note_content = get_range_by_name(ir, "note_content")
    note_title = get_range_by_name(ir, "note_title")
    new_contents = []
    new_titles = []
    for indx, (note_con, note_tit) in enumerate(
        zip(note_content["values"], note_title["values"])
    ):
        new_contents.append(str(note_con).strip())
        new_titles.append(str(note_tit).strip())

    new_ir = replace_range_by_name(ir, "note_content", new_contents)
    new_ir = replace_range_by_name(new_ir, "note_title", new_titles)

    return new_ir
