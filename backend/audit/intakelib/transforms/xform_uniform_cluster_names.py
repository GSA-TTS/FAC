import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
)

logger = logging.getLogger(__name__)


def regenerate_uniform_cluster_names(ir):
    state_cluster_names = get_range_by_name(ir, "state_cluster_name")
    other_cluster_names = get_range_by_name(ir, "other_cluster_name")
    uniform_state_cluster_name_values = [
        None if v is None or not str(v).strip() else str(v).strip().upper()
        for v in state_cluster_names["values"]
    ]
    uniform_other_cluster_name_values = [
        None if v is None or not str(v).strip() else str(v).strip().upper()
        for v in other_cluster_names["values"]
    ]
    new_ir = replace_range_by_name(
        ir, "uniform_state_cluster_name", uniform_state_cluster_name_values
    )
    xform_ir = replace_range_by_name(
        new_ir, "uniform_other_cluster_name", uniform_other_cluster_name_values
    )
    return xform_ir
