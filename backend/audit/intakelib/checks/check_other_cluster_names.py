import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name
) 
from .util import (
    get_message,
    build_cell_error_tuple
    )

logger = logging.getLogger(__name__)

OTHER_CLUSTER = 'OTHER CLUSTER NOT LISTED ABOVE'

def other_cluster_names(ir):
    cluster_name = get_range_by_name(ir, "cluster_name")
    state_cluster_name = get_range_by_name(ir, "state_cluster_name")
    other_cluster_name = get_range_by_name(ir, "other_cluster_name")
    
    errors = []

    for ndx, cn, scn, ocn in zip(range(len(cluster_name["values"])), 
                                 cluster_name["values"],
                                 state_cluster_name["values"],
                                 other_cluster_name["values"]):
        if (cn == OTHER_CLUSTER):
            # If they indicated other cluster, then it should be populated.
            if not ocn:
                errors.append(build_cell_error_tuple(ir,
                                                     cluster_name,
                                                     ndx,
                                                     get_message("check_other_cluster_names_cluster_name_missing")
                                                     ))
        elif (cn and ocn):
            # If it is a cluster name, but they include other cluster, that's a problem.
            errors.append(build_cell_error_tuple(ir,
                                                    cluster_name,
                                                    ndx,
                                                    get_message("check_other_cluster_names_no_other_cluster_needed")
                                                    ))


    return errors
