from django.core.exceptions import ValidationError
import logging
from copy import deepcopy
from pprint import pprint

logger = logging.getLogger(__name__)

def run_all_transforms(ir, list_of_xforms):
    new_ir = deepcopy(ir)
    print("========== DEEP COPY ===========")
    pprint(new_ir)
    for fun in list_of_xforms:
        new_ir = fun(new_ir)
    return new_ir

def run_all_notes_to_sefa_transforms(ir):
    return run_all_transforms(ir, notes_to_sefa_transforms)

from .xform_no_op import no_op

general_transforms = [ no_op ]

from .xform_replace_seq_numbers_in_notes_to_sefa import replace_seq_numbers_in_notes_to_sefa

notes_to_sefa_transforms = general_transforms + [
    replace_seq_numbers_in_notes_to_sefa
]
