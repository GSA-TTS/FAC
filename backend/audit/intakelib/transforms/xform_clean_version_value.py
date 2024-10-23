import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
)

logger = logging.getLogger(__name__)


def remove_equals_and_quotes(ir):
    versions = get_range_by_name(ir, "version")
    new_values = list(
        map(
            lambda v: v.replace("=", "").replace('"', "") if v else v,
            versions["values"],
        )
    )
    new_ir = replace_range_by_name(ir, "version", new_values)

    return new_ir
