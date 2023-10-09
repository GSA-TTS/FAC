from django.core.exceptions import ValidationError
import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


def cluster_name_always_present(ir):
    cn = get_range_by_name(ir, "cluster_name")
    errors = []
    for ndx, v in enumerate(cn["values"]):
        if (v is None) or (str(v).strip() == ""):
            errors.append(
                build_cell_error_tuple(
                    ir, cn, ndx, get_message("check_cluster_name_always_present")
                )
            )

    return errors
