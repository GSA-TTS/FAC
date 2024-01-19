import logging
from django.core.exceptions import ValidationError
import re
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
)
from audit.intakelib.common import (
    get_message,
    build_cell_error_tuple,
    appears_empty,
)

logger = logging.getLogger(__name__)

# A version of these regexes also exists in Base.libsonnet
FINDING_REFERENCE_REGEX = r"^20[1-9][0-9]-[0-9]{3}(,\s*20[1-9][0-9]-[0-9]{3})*$"


# DESCRIPTION
# Finding references should be in 20##-### format where the first four
# digits are a year >= 2010.
# TESTED BY
# has_bad_references.xlsx
def finding_reference_pattern(ir):
    references = get_range_by_name(ir, "reference_number")
    errors = []
    for index, reference in enumerate(references["values"]):
        if not appears_empty(reference) and (
            not re.match(FINDING_REFERENCE_REGEX, str(reference))
        ):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    references,
                    index,
                    get_message("check_finding_reference_invalid"),
                )
            )

    if len(errors) > 0:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)
