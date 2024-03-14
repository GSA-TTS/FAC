from django.core.exceptions import ValidationError
import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
)
from audit.intakelib.common import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)

AUTHORIZED_VERSIONS = {"1.0.0", "1.0.1", "1.0.2", "1.0.3", "1.0.4", "1.0.5"}


# DESCRIPTION
# This checks if the uploaded workbook version is valid.
def validate_workbook_version(ir):
    version_range = get_range_by_name(ir, "version")
    errors = []
    for index, version in enumerate(version_range["values"]):
        # Check if version is not in the set of valid versions
        if version not in AUTHORIZED_VERSIONS:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    version_range,
                    index,
                    get_message("check_workbook_version").format(version),
                )
            )

    if errors:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)
