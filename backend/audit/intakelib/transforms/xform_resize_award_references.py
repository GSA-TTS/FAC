import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
)
from audit.intakelib.checks.check_finding_award_references_pattern import (
    AWARD_LEN_5_DIGITS,
)

logger = logging.getLogger(__name__)

AWARD_REFERENCE_PREFIX = "AWARD"


def resize_award_reference(ir):
    references = get_range_by_name(ir, "award_reference")
    new_values = list(map(_format_reference, references["values"]))
    new_ir = replace_range_by_name(ir, "award_reference", new_values)

    return new_ir


def _format_reference(v):
    """Format the award reference to have 5 digits, padding with zeros if necessary"""
    if not v or len(v) >= AWARD_LEN_5_DIGITS:
        return v

    parts = v.split("-")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return v

    prefix, number = parts
    if prefix.upper() != AWARD_REFERENCE_PREFIX:
        return v

    padding = "0" * (AWARD_LEN_5_DIGITS - len(v))
    return f"{prefix}-{padding}{number}"
