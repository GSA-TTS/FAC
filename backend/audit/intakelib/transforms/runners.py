import logging
from copy import deepcopy

from .xform_no_op import no_op

from .xform_replace_seq_numbers_in_notes_to_sefa import (
    replace_seq_numbers_in_notes_to_sefa,
)

logger = logging.getLogger(__name__)


def run_all_transforms(ir, list_of_xforms):
    new_ir = deepcopy(ir)
    for fun in list_of_xforms:
        new_ir = fun(new_ir)
    return new_ir


def run_all_notes_to_sefa_transforms(ir):
    return run_all_transforms(ir, notes_to_sefa_transforms)


general_transforms = [no_op]

notes_to_sefa_transforms = general_transforms + [replace_seq_numbers_in_notes_to_sefa]
