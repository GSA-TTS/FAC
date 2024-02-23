import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
)
from audit.intakelib.common import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


# DESCRIPTION
# if passthrough_name and passthrough_identifying_number are not empty,
# then check if the tuple (passthrough_name, passthrough_identifying_number) is unique
def passthrough_names_and_ids_uniqueness(ir):
    """Check if the tuple (passthrough_name, passthrough_identifying_number) is unique."""
    passthrough_names = get_range_by_name(ir, "passthrough_name")
    passthrough_identifying_numbers = get_range_by_name(
        ir, "passthrough_identifying_number"
    )

    errors = []
    seen = set()

    for index, (pass_name, pass_id) in enumerate(
        zip(passthrough_names["values"], passthrough_identifying_numbers["values"])
    ):
        if pass_name and pass_id:
            names = pass_name.split("|")
            ids = pass_id.split("|")
            # The assumption here is that the number of names and IDs are the same.
            # This is enforced by the check_cardinality_of_passthrough_names_and_ids check
            # and by the xform_fill_missing_passthrough_ids_with_na transformation.

            for name, id in zip(names, ids):
                if (name, id) in seen:
                    errors.append(
                        build_cell_error_tuple(
                            ir,
                            passthrough_names,
                            index,
                            get_message(
                                "check_passthrough_names_and_ids_uniqueness"
                            ).format(name, id),
                        )
                    )
                seen.add((name, id))

    return errors
