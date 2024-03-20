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
AWARD_REFERENCES_REGEX4 = r"^AWARD-(?!0{4}$)[0-9]{4}$"
AWARD_REFERENCES_REGEX5 = r"^AWARD-(?!0{5}$)[0-9]{5}$"


# DESCRIPTION
# Award references should be of format AWARD-#### or AWARD-#####
# TESTED BY
# has_bad_award_references.xlsx
def award_references_pattern(ir):
    award_references = get_range_by_name(ir, "award_reference")
    errors = []
    count_length_4 = 0
    count_length_5 = 0

    for index, award_reference in enumerate(award_references["values"]):
        if len(award_reference) == 10:
            count_length_4 += 1
        elif len(award_reference) == 11:
            count_length_5 += 1
        else:
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

    # Decide on what to look for, based on the preponderance of lengths.
    if count_length_4 > count_length_5:
        THE_REGEX = AWARD_REFERENCES_REGEX4
        pattern = "AWARD-####"
        example = "AWARD-0042"
    else:
        THE_REGEX = AWARD_REFERENCES_REGEX5
        pattern = "AWARD-#####"
        example = "AWARD-00042"

    for index, award_reference in enumerate(award_references["values"]):
        if not re.match(THE_REGEX, str(award_reference)):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    award_references,
                    index,
                    get_message("check_award_references_invalid").format(
                        pattern, example
                    ),
                )
            )

    if len(errors) > 0:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)
