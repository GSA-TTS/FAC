import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from .util import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)

STATE_CLUSTER = "STATE CLUSTER"


def state_cluster_names(ir):
    cluster_name = get_range_by_name(ir, "cluster_name")
    state_cluster_name = get_range_by_name(ir, "state_cluster_name")

    errors = []

    for ndx, cn, scn in zip(
        range(len(cluster_name["values"])),
        cluster_name["values"],
        state_cluster_name["values"],
    ):

        if cn == STATE_CLUSTER:
            # If they indicated state cluster, then it should be populated.
            if not scn:
                errors.append(
                    build_cell_error_tuple(
                        ir,
                        cluster_name,
                        ndx,
                        get_message("check_cluster_names_state_cluster_missing"),
                    )
                )
        elif cn and scn:
            # If it is a cluster name, but they include state cluster, that's a problem.
            errors.append(
                build_cell_error_tuple(
                    ir,
                    cluster_name,
                    ndx,
                    get_message("check_cluster_names_no_state_cluster_needed"),
                )
            )
    return errors
