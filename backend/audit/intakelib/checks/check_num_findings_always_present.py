from django.core.exceptions import ValidationError
import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


def num_findings_always_present(ir):
    noaf = get_range_by_name(ir, "number_of_audit_findings")
    errors = []
    for ndx, v in enumerate(noaf["values"]):
        if ((v is None) or (str(v).strip() == "")):
            errors.append(
                build_cell_error_tuple(
                    ir, noaf, ndx, 
                    get_message("check_num_findings_always_present")
                )
            )

    return errors

