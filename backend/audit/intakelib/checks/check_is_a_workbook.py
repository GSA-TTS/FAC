from django.core.exceptions import ValidationError
import logging
from audit.intakelib.intermediate_representation import (
    get_sheet_by_name,
    get_range_by_name,
)

logger = logging.getLogger(__name__)


# DESCRIPTION
# Checks that this is a workbook.
# Does this by checking for the coversheet.
# Correctly fails to validate workbooks that are really
# sloppy and still have a coversheet page.
def is_a_workbook(ir):
    coversheet = get_sheet_by_name(ir, "Coversheet")
    version_range = get_range_by_name(ir, "version")
    if not (coversheet and version_range):
        raise ValidationError(
            (
                "(O_o)",
                "",
                "Not a FAC workbook",
                {
                    "text": "This does not appear to be a FAC workbook",
                    "link": "Intake checks: no link defined",
                },
            )
        )
