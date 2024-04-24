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
    is_value_marked_na,
)

logger = logging.getLogger(__name__)

# A version of these regexes also exists in Base.libsonnet
PRIOR_REFERENCES_REGEX = r"^[1-2][0-9]{3}-[0-9]{3}(,\s*[1-2][0-9]{3}-[0-9]{3})*$"


# DESCRIPTION
# Prior references should be a comma separated list of 20##-### values
# TESTED BY
# has_bad_prior_references.xlsx
def prior_references_pattern(ir):
    prior_references = get_range_by_name(ir, "prior_references")
    errors = []
    for index, prior_reference in enumerate(prior_references["values"]):
        if (
            not appears_empty(prior_reference)
            and (not is_value_marked_na(prior_reference))
            and (not re.match(PRIOR_REFERENCES_REGEX, str(prior_reference)))
        ):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    prior_references,
                    index,
                    get_message("check_prior_references_invalid"),
                )
            )

    if len(errors) > 0:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)
