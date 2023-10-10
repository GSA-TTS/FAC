import logging
from audit.intakelib.intermediate_representation import get_range_values_by_name
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)

# DESCRIPTION
# This makes sure that every value in the award_reference column
# is a unique value. 
# WHY
# Some users manage to unlock the awards sheet, and then can delete rows
# and modify this column (which is normally auto-generated and locked).
# Therefore, we have to check the values are what we expect.
def all_unique_award_numbers(ir):
    award_references = get_range_values_by_name(ir, "award_reference")
    errors = []
    found = []
    for index, award_ref in enumerate(award_references):
        if award_ref in found:
            errors.append(
                build_cell_error_tuple(
                    ir, award_references, index, get_message("check_all_unique_award_numbers")
                )
            )
        if award_ref not in found:
            found.append(award_ref)
    return errors
