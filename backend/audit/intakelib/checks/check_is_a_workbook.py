from django.core.exceptions import ValidationError
import logging
from audit.intakelib.intermediate_representation import get_sheet_by_name

logger = logging.getLogger(__name__)


def is_a_workbook(ir):
    coversheet = get_sheet_by_name(ir, "Coversheet")
    if not coversheet:
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
