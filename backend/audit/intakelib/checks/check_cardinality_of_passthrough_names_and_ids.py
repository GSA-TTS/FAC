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
    passthrough_names = get_range_by_name(ir, "passthrough_name").get("values")
    passthrough_identifying_numbers = get_range_by_name(
        ir, "passthrough_identifying_number"
    ).get("values")
    # This is needed to avoid None values to bypass the check
    passthrough_names = [value if value else "" for value in passthrough_names]
    passthrough_identifying_numbers = [
        value if value else "" for value in passthrough_identifying_numbers
    ]
    errors = []

    for index, (pass_name, pass_id) in enumerate(
        zip(passthrough_names, passthrough_identifying_numbers)
    ):
        if (pass_name or pass_id) and ("|" in pass_name or "|" in pass_id):
            names = [value.strip() for value in pass_name.split("|")]
            ids = [value.strip() for value in pass_id.split("|")]
            if "" in names:
                errors.append(
                    build_cell_error_tuple(
                        ir,
                        get_range_by_name(ir, "passthrough_name"),
                        index,
                        get_message("check_blank_space_in_passthrough_names"),
                    )
                )
            if "" in ids:
                errors.append(
                    build_cell_error_tuple(
                        ir,
                        get_range_by_name(ir, "passthrough_identifying_number"),
                        index,
                        get_message(
                            "check_blank_space_in_passthrough_identifying_numbers"
                        ),
                    )
                )
            # print(names, ids)
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
