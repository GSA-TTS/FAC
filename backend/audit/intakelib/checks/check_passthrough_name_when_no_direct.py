import logging

from django.conf import settings
from audit.intakelib.intermediate_representation import get_range_by_name
from audit.intakelib.common import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


def appears_empty(v):
    return (v is None) or (str(v).strip() == "")


def passthrough_name_when_no_direct(ir):
    is_direct = get_range_by_name(ir, "is_direct")
    passthrough_name = get_range_by_name(ir, "passthrough_name")
    passthrough_number = get_range_by_name(ir, "passthrough_identifying_number")

    errors = []
    for ndx, (isd, pname, pnum) in enumerate(
        zip(
            is_direct["values"],
            passthrough_name["values"],
            passthrough_number["values"],
        )
    ):
        if (isd == "Y") and (pnum is not None):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    passthrough_number,
                    ndx,
                    get_message(
                        "check_passthrough_name_when_no_direct_n_and_empty_number"
                    ),
                )
            )

        elif (isd == "N") and (pname is None):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    is_direct,
                    ndx,
                    get_message("check_passthrough_name_when_no_direct"),
                )
            )
        elif (isd == "Y") and pname:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    is_direct,
                    ndx,
                    get_message("check_passthrough_name_when_yes_direct"),
                )
            )
        elif (isd == settings.GSA_MIGRATION) and (not pname):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    is_direct,
                    ndx,
                    get_message("check_passthrough_name_when_invalid_direct"),
                )
            )

    return errors
