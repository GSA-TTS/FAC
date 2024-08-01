from django.core.exceptions import ValidationError
import logging
from audit.intakelib.intermediate_representation import (
    get_range_values_by_name,
    get_range_by_name,
)
from audit.intakelib.common import get_message, build_cell_error_tuple
from audit.fixtures.excel import FORM_SECTIONS

logger = logging.getLogger(__name__)

FEDERAL_AWARDS_EXPENDED = "FederalAwardsExpended"

# DESCRIPTION
# Makes sure we're looking at the right workbook.
# WHY?
# First, we have workbook-specific error checks.
# Actually, that's the main reason.
def is_right_workbook(what_this_section_should_be):
    def _check_ir(ir):
        section_name = get_range_values_by_name(ir, "section_name")
        expected_section_name = what_this_section_should_be
        # If the expected section name is FEDERAL_AWARDS, we need to check the version number
        # to determine if we should be looking at FEDERAL_AWARDS or FEDERAL_AWARDS_EXPENDED
        if expected_section_name == FORM_SECTIONS.FEDERAL_AWARDS:
            version_range = get_range_by_name(ir, "version")
            version = version_range["values"][0]
            if int(version.replace(".", "")) < 112:
                expected_section_name = FEDERAL_AWARDS_EXPENDED

        if (section_name) and (expected_section_name not in section_name):
            raise ValidationError(
                build_cell_error_tuple(
                    ir,
                    get_range_by_name(ir, "section_name"),
                    0,
                    get_message("check_is_right_workbook").format(
                        expected_section_name
                    ),
                )
            )

    return _check_ir
