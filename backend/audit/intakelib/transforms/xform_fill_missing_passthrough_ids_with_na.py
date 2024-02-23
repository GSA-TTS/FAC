import logging

from django.conf import settings
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
)

logger = logging.getLogger(__name__)


def fill_missing_passthrough_ids_with_na(ir):
    """Update the identifying numbers for passthrough entities in the intermediate representation (ir).
    If a passthrough entity does not have an identifying number and is not direct, set its ID to 'N/A'
    """
    direct_awards = get_range_by_name(ir, "is_direct")
    passthrough_names = get_range_by_name(ir, "passthrough_name")
    identifying_numbers = get_range_by_name(ir, "passthrough_identifying_number")
    new_ids_values = []
    if identifying_numbers["values"] or passthrough_names["values"]:
        for is_direct, name, id in zip(
            direct_awards["values"],
            passthrough_names["values"],
            identifying_numbers["values"],
        ):
            if is_direct == "N" and name and "|" not in name and not id:
                # name is not empty but id is missing
                new_ids_values.append(settings.NOT_APPLICABLE)
            else:
                new_ids_values.append(id)

        updated_ir = replace_range_by_name(
            ir, "passthrough_identifying_number", new_ids_values
        )

        return updated_ir
    # Return the original input record if no updates are necessary
    return ir
