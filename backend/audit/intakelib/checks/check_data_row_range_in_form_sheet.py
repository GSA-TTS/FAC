from django.conf import settings
from django.core.exceptions import ValidationError
import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
)
from audit.intakelib.common import get_message, build_cell_error_tuple


logger = logging.getLogger(__name__)


def validate_ranges(ir):
    """Validate the ranges of the data columns based on the version of the workbook.
    The row numbers must be at most 10000 for versions 1.0.0 to 1.0.5 and at most 20000 for version 1.1.0.
    """
    errors = []
    for sheet in ir:
        # only process sheet with name equal 'Form'

        if sheet["name"] == "Form":
            version_range = get_range_by_name(ir, "version")
            version = version_range["values"][0]
            version_tuple = tuple(map(int, version.split(".")))

            for range_info in sheet["ranges"]:
                name = range_info["name"]
                start_row = int(range_info["start_cell"]["row"])
                end_row = int(range_info["end_cell"]["row"])

                total_rows = end_row - start_row + 1

                if (
                    version_tuple <= (1, 0, 5)
                    and total_rows > settings.DEFAULT_MAX_ROWS
                ):
                    errors.append(
                        build_cell_error_tuple(
                            ir,
                            range_info,
                            0,
                            get_message("check_max_rows").format(name),
                        )
                    )

                elif version_tuple >= (1, 1, 0) and total_rows > settings.MAX_ROWS:
                    errors.append(
                        build_cell_error_tuple(
                            ir,
                            range_info,
                            0,
                            get_message("check_max_rows").format(name),
                        )
                    )

    if errors:
        logger.info("Raising a validation error.")

        raise ValidationError(errors)
