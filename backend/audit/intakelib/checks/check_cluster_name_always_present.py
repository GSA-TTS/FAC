import logging
from audit.intakelib.intermediate_representation import (
    get_range_values_by_name,
    get_range_by_name
    )
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)

# DESCRIPTION
# The cluster name should always be present. It is either
# a cluster name or `N/A`, but never empty.
# WHY
# People sometimes leave it empty instead of N/A.
def cluster_name_always_present(ir):
    cluster_names = get_range_values_by_name(ir, "cluster_name")
    errors = []
    for index, cluster_name in enumerate(cluster_names):
        if (cluster_name is None) or (str(cluster_name).strip() == ""):
            errors.append(
                build_cell_error_tuple(
                    ir, get_range_by_name(ir, "cluster_name"), index, get_message("check_cluster_name_always_present")
                )
            )

    return errors
