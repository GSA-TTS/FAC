import json
import logging

from django.conf import settings
from audit.intakelib.intermediate_representation import get_range_by_name
from audit.intakelib.common import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)


def check_cluster_names(ir):
    """Check that cluster names are valid when present."""

    range_data = get_range_by_name(ir, "cluster_name")
    errors = []
    if range_data and ("values" in range_data):
        try:
            with open(f"{settings.SCHEMA_BASE_DIR}/ClusterNames.json") as valid_file:
                valid_json = json.load(valid_file)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"ClusterNames.json file not found in {settings.SCHEMA_BASE_DIR}/ClusterNames.json."
            )
        except json.decoder.JSONDecodeError:
            raise ValueError("ClusterNames.json file contains invalid JSON.")

        for index, value in enumerate(range_data["values"]):
            if value and value not in valid_json["cluster_names"]:
                errors.append(
                    build_cell_error_tuple(
                        ir,
                        range_data,
                        index,
                        get_message("check_cluster_names"),
                    )
                )

    return errors
