import logging
from copy import deepcopy
from audit.intakelib.intermediate_representation import (
    replace_range_by_name,
)

logger = logging.getLogger(__name__)


# DESCRIPTION
# Strip all text fields of leading and trailing whitespace
def convert_to_stripped_string(ir):
    new_ir = deepcopy(ir)
    for sheet in ir:
        # To ensure backwards compatibility with NotesToSefa workbook 1.0.0 and 1.0.1, we check for both "AdditionalNotes" and "Form"
        if sheet["name"] in {"AdditionalNotes", "Form", "Coversheet"}:
            for range in sheet["ranges"]:
                formatted_values = [
                    None if v is None or (not str(v).strip()) else str(v).strip()
                    for v in range["values"]
                ]
                new_ir = replace_range_by_name(new_ir, range["name"], formatted_values)
    return new_ir
