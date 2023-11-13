import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
)
from audit.intakelib.common import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


# DESCRIPTION
# If users provide a `|` in the passthrough id number field,
# we expect multiple names in the name field, too.
def cardinality_of_passthrough_names_and_ids(ir):
    passthrough_name = get_range_by_name(ir, "passthrough_name")
    passthrough_identifying_number = get_range_by_name(
        ir, "passthrough_identifying_number"
    )

    errors = []

    for index, (pass_name, pass_id) in enumerate(
        zip(passthrough_name["values"], passthrough_identifying_number["values"])
    ):
        if (pass_name and pass_id) and ("|" in pass_name or "|" in pass_id):
            names = pass_name.split("|")
            ids = pass_id.split("|")
            print(names, ids)
            if len(names) != len(ids):
                errors.append(
                    build_cell_error_tuple(
                        ir,
                        get_range_by_name(ir, "passthrough_name"),
                        index,
                        (
                            get_message(
                                "check_cardinality_of_passthrough_names_and_ids"
                            ).format(
                                len(names),
                                "s" if len(names) > 1 else "",
                                len(ids),
                                "s" if len(ids) > 1 else "",
                            )
                        ),
                    )
                )

    return errors
