import logging

from django.conf import settings
from audit.intakelib.intermediate_representation import (
    get_range_values_by_name,
    get_range_by_name,
)
from audit.intakelib.common import get_message, build_cell_error_tuple
from census_historical_migration.invalid_record import InvalidRecord

logger = logging.getLogger(__name__)


# DESCRIPTION
# The sum of the amount_expended for a given cluster should equal the corresponding cluster_total
# K{0}=IF(G{0}="OTHER CLUSTER NOT LISTED ABOVE",SUMIFS(amount_expended,uniform_other_cluster_name,X{0}),IF(AND(OR(G{0}="N/A",G{0}=""),H{0}=""),0,IF(G{0}="STATE CLUSTER",SUMIFS(amount_expended,uniform_state_cluster_name,W{0}),SUMIFS(amount_expended,cluster_name,G{0}))))
def cluster_total_is_correct(ir, is_data_migration=False):
    uniform_other_cluster_names = get_range_values_by_name(
        ir, "uniform_other_cluster_name"
    )
    uniform_state_cluster_names = get_range_values_by_name(
        ir, "uniform_state_cluster_name"
    )
    state_cluster_names = get_range_values_by_name(ir, "state_cluster_name")
    cluster_names = get_range_values_by_name(ir, "cluster_name")
    cluster_totals = get_range_values_by_name(ir, "cluster_total")
    amounts_expended = get_range_values_by_name(ir, "amount_expended")

    errors = []

    if (
        is_data_migration
        and "cluster_total_is_correct"
        in InvalidRecord.fields["validations_to_skip"]
    ):
        # Skip this validation if it is an historical audit report with incorrect cluster total
        return errors

    # Validating each cluster_total
    for idx, name in enumerate(cluster_names):
        # Check if the calculated value matches the provided one
        expected_value = expected_cluster_total(
            idx=idx,
            name=name,
            uniform_other_cluster_names=uniform_other_cluster_names,
            uniform_state_cluster_names=uniform_state_cluster_names,
            state_cluster_names=state_cluster_names,
            cluster_names=cluster_names,
            amounts_expended=amounts_expended,
        )
        if expected_value != cluster_totals[idx]:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    get_range_by_name(ir, "cluster_total"),
                    idx,
                    get_message("check_cluster_total").format(
                        cluster_totals[idx], expected_value
                    ),
                )
            )

    return errors


def expected_cluster_total(**kwargs):
    # idx, name, uniform_other_cluster_names, uniform_state_cluster_names, state_cluster_names, cluster_names, amounts_expended
    # Get the values from the kwargs
    idx = kwargs.get("idx")
    name = kwargs.get("name")
    uniform_other_cluster_names = kwargs.get("uniform_other_cluster_names")
    uniform_state_cluster_names = kwargs.get("uniform_state_cluster_names")
    state_cluster_names = kwargs.get("state_cluster_names")
    cluster_names = kwargs.get("cluster_names")
    amounts_expended = kwargs.get("amounts_expended")

    # Based on the formula's conditions
    if name == settings.OTHER_CLUSTER:
        expected_value = sum(
            [
                amount
                for k, amount in zip(uniform_other_cluster_names, amounts_expended)
                if k == uniform_other_cluster_names[idx]
            ]
        )
    elif (
        name is None
        or str(name).strip() == ""
        or name == settings.NOT_APPLICABLE
        or name == settings.GSA_MIGRATION
    ) and (
        state_cluster_names[idx] is None or str(state_cluster_names[idx]).strip() == ""
    ):
        expected_value = 0
    elif name == settings.STATE_CLUSTER:
        expected_value = sum(
            [
                amount
                for k, amount in zip(uniform_state_cluster_names, amounts_expended)
                if k == uniform_state_cluster_names[idx]
            ]
        )
    elif name:
        expected_value = sum(
            [amount for k, amount in zip(cluster_names, amounts_expended) if k == name]
        )
    else:
        expected_value = 0

    return expected_value
