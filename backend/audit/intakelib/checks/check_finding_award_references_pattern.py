import logging
from django.core.exceptions import ValidationError
import re
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
)
from audit.intakelib.common import (
    get_message,
    build_cell_error_tuple,
)

logger = logging.getLogger(__name__)

# A version of this regex also exists in Base.libsonnet
AWARD_REFERENCES_REGEX = r"^AWARD-(?!0{4,5}$)[0-9]{4,5}$"
AWARD_REFERENCES_REGEX5 = r"^AWARD-(?!0{5}$)[0-9]{5}$"

AWARD_LEN_4_DIGITS = 10
AWARD_LEN_5_DIGITS = 11


# DESCRIPTION
# Award references should be of format AWARD-#### or AWARD-#####
# TESTED BY
# has_bad_award_references.xlsx
def award_references_pattern(ir):
    award_references = get_range_by_name(ir, "award_reference")
    errors = []
    count_length_5 = 0

    for index, award_reference in enumerate(award_references["values"]):
        if len(award_reference) == AWARD_LEN_5_DIGITS:
            count_length_5 += 1

        if not re.match(AWARD_REFERENCES_REGEX, str(award_reference)):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    award_references,
                    index,
                    get_message("check_award_references_len_4_or_5").format(
                        award_reference
                    ),
                )
            )

    # If there are any with 5 digits, they all must have 5 digits
    if count_length_5:
        for index, award_reference in enumerate(award_references["values"]):
            if len(award_reference) == AWARD_LEN_4_DIGITS:
                errors.append(
                    build_cell_error_tuple(
                        ir,
                        award_references,
                        index,
                        get_message("check_award_references_invalid"),
                    )
                )

    if len(errors) > 0:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)
