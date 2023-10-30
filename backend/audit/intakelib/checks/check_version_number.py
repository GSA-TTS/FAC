from django.core.exceptions import ValidationError
import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
)
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)

AUTHORIZED_VERSIONS = {"1.0.0", "1.0.1", "1.0.2"}


# DESCRIPTION
# This is intended to be a check for the version number of the workbook.
def validate_workbook_version(ir):
    # FIXME: This is a no-op for now. Remove below pass when ready to enforce version check.
    pass

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
