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


# DESCRIPTION
# Award references should be of format AWARD-#### or AWARD-#####
# TESTED BY
# has_bad_award_references.xlsx
def award_references_pattern(ir):
    award_references = get_range_by_name(ir, "award_reference")
    errors = []
    for index, award_reference in enumerate(award_references["values"]):
        if not re.match(AWARD_REFERENCES_REGEX, str(award_reference)):
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
