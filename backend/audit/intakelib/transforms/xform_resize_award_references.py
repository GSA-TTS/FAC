import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
)
from audit.intakelib.checks.check_finding_award_references_pattern import (
    AWARD_LEN_5_DIGITS,
)

logger = logging.getLogger(__name__)


def resize_award_reference(ir):
    references = get_range_by_name(ir, "award_reference")
    new_values = list(map(_format_reference, references["values"]))
    new_ir = replace_range_by_name(ir, "award_reference", new_values)

    return new_ir


def _format_reference(v):

    if v and len(v) < AWARD_LEN_5_DIGITS:
        parts = v.split("-")
        padding = "0" * (AWARD_LEN_5_DIGITS - len(v))
        return f"{parts[0]}-{padding}{parts[1]}"
    return v
