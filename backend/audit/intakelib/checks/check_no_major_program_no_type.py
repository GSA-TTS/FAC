import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


def no_major_program_no_type(ir):
    is_major = get_range_by_name(ir, "is_major")
    audit_report_type = get_range_by_name(ir, "audit_report_type")

    errors = []

    for ndx, (is_m, rep_type) in enumerate(
        zip(is_major["values"], audit_report_type["values"])
    ):
        if (is_m == "N") and rep_type:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    audit_report_type,
                    ndx,
                    get_message("check_no_major_program_no_type_when_n"),
                )
            )
        elif (is_m == "Y") and not rep_type:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    audit_report_type,
                    ndx,
                    get_message("check_no_major_program_no_type_when_y"),
                )
            )

    return errors
