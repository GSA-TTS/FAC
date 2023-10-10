from django.core.exceptions import ValidationError
import logging
from audit.intakelib.intermediate_representation import get_range_values_by_name
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)

# DESCRIPTION
# Makes sure we're looking at the right workbook.
# WHY?
# First, we have workbook-specific error checks.
# Actually, that's the main reason.
def is_right_workbook(what_this_section_should_be):
    def _check_ir(ir):
        section_name = get_range_values_by_name(ir, "section_name")
        if (section_name) and (what_this_section_should_be not in section_name):
            raise ValidationError(
                build_cell_error_tuple(
                    ir,
                    section_name,
                    0,
                    get_message("check_is_right_workbook").format(what_this_section_should_be),
                )
            )

    return _check_ir
