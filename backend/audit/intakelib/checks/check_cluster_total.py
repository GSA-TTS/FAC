import logging
from audit.intakelib.intermediate_representation import (
    get_range_values_by_name,
    get_range_by_name,
)
from audit.intakelib.common import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)

STATE_CLUSTER = "STATE CLUSTER"
OTHER_CLUSTER = "OTHER CLUSTER NOT LISTED ABOVE"
NOT_APPLICABLE = "N/A"


# DESCRIPTION
# The sum of the amount_expended for a given cluster should equal the corresponding cluster_total
# K{0}=IF(G{0}="OTHER CLUSTER NOT LISTED ABOVE",SUMIFS(amount_expended,uniform_other_cluster_name,X{0}),IF(AND(OR(G{0}="N/A",G{0}=""),H{0}=""),0,IF(G{0}="STATE CLUSTER",SUMIFS(amount_expended,uniform_state_cluster_name,W{0}),SUMIFS(amount_expended,cluster_name,G{0}))))
def cluster_total_is_correct(ir):
    uniform_other_cluster_name = get_range_values_by_name(
        ir, "uniform_other_cluster_name"
    )
    uniform_state_cluster_name = get_range_values_by_name(
        ir, "uniform_state_cluster_name"
    )
    state_cluster_name = get_range_values_by_name(ir, "state_cluster_name")
    cluster_name = get_range_values_by_name(ir, "cluster_name")
    cluster_total = get_range_values_by_name(ir, "cluster_total")
    amount_expended = get_range_values_by_name(ir, "amount_expended")

    errors = []

    # Validating each cluster_total
    for idx, name in enumerate(cluster_name):
        # Based on the formula's conditions
        if name == OTHER_CLUSTER:
            expected_value = sum(
                [
                    amount
                    for k, amount in zip(uniform_other_cluster_name, amount_expended)
                    if k == uniform_other_cluster_name[idx]
                ]
            )
        elif (name is None or str(name).strip() == "" or name == NOT_APPLICABLE) and (
            state_cluster_name[idx] is None
            or str(state_cluster_name[idx]).strip() == ""
        ):
            expected_value = 0
        elif name == STATE_CLUSTER:
            expected_value = sum(
                [
                    amount
                    for k, amount in zip(uniform_state_cluster_name, amount_expended)
                    if k == uniform_state_cluster_name[idx]
                ]
            )
        elif name:
            expected_value = sum(
                [
                    amount
                    for k, amount in zip(cluster_name, amount_expended)
                    if k == name
                ]
            )
        else:
            expected_value = 0
        # Check if the calculated value matches the provided one
        if expected_value != cluster_total[idx]:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    get_range_by_name(ir, "cluster_total"),
                    idx,
                    get_message("check_cluster_total").format(
                        cluster_total[idx], expected_value
                    ),
                )
            )

    return errors
