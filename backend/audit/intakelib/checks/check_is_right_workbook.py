from django.core.exceptions import ValidationError
import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


def is_right_workbook(this_should_be):
    def _check_ir(ir):
        section_name = get_range_by_name(ir, "section_name")
        if (section_name) and this_should_be not in section_name["values"]:
            raise ValidationError(
                build_cell_error_tuple(
                    ir,
                    section_name,
                    0,
                    get_message("check_is_right_workbook").format(this_should_be),
                )
            )

    return _check_ir
