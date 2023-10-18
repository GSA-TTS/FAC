import logging
from copy import deepcopy

from .xform_no_op import no_op

from .xform_insert_sequence_nums_into_notes_to_sefa import (
    insert_sequence_nums_into_notes_to_sefa,
)

# from .xform_filter_seq_numbers_where_there_are_no_values import filter_seq_numbers_where_there_are_no_values
# from .xform_make_sure_notes_to_sefa_are_just_strings import make_sure_notes_to_sefa_are_just_strings
from .xform_trim_null_from_content_fields_in_notes_to_sefa import (
    trim_null_from_content_fields_in_notes_to_sefa,
)

from .xform_eins_need_to_be_strings import eins_need_to_be_strings
from .xform_rename_additional_notes_sheet import (
    rename_additional_notes_sheet_to_form_sheet,
)

logger = logging.getLogger(__name__)


def run_all_transforms(ir, list_of_xforms):
    new_ir = deepcopy(ir)
    for fun in list_of_xforms:
        new_ir = fun(new_ir)
    return new_ir


def run_all_notes_to_sefa_transforms(ir):
    return run_all_transforms(ir, notes_to_sefa_transforms)


def run_all_additional_eins_transforms(ir):
    return run_all_transforms(ir, additional_eins_transforms)


general_transforms = [no_op]

notes_to_sefa_transforms = general_transforms + [
    trim_null_from_content_fields_in_notes_to_sefa,
    rename_additional_notes_sheet_to_form_sheet,
    insert_sequence_nums_into_notes_to_sefa,
]

additional_eins_transforms = general_transforms + [
    eins_need_to_be_strings,
]
