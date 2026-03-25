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
from django.conf import settings

logger = logging.getLogger(__name__)

# A version of these regexes also exists in Base.libsonnet
FINDING_REFERENCE_REGEX = r"^[1-2][0-9]{3}-[0-9]{3}(,\s*[1-2][0-9]{3}-[0-9]{3})*$"


# DESCRIPTION
# Finding references should be in 20##-### format where the first four
# digits are a year >= 1900.
def finding_reference_pattern(ir, is_gsa_migration=False):
    references = get_range_by_name(ir, "reference_number")
    errors = []
    for index, reference in enumerate(references["values"]):
        is_empty = appears_empty(reference)
        is_valid_format = is_empty or re.match(FINDING_REFERENCE_REGEX, str(reference))
        is_valid_migration = reference == settings.GSA_MIGRATION and is_gsa_migration

        if not (is_valid_format or is_valid_migration):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    references,
                    index,
                    get_message("check_finding_reference_invalid"),
                )
            )

    if len(errors) > 0:
        raise ValidationError(errors)
