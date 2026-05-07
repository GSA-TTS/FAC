from django.core.exceptions import ValidationError
import json
import logging
from pathlib import Path

from audit.intakelib.intermediate_representation import (
    get_range_by_name,
)
from audit.intakelib.common import get_message, build_cell_error_tuple

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parents[3]
VERSION_FILE = BACKEND_DIR / "schemas" / "source" / "data" / "workbook_version.json"

with VERSION_FILE.open("r", encoding="utf-8") as f:
    workbook_version_config = json.load(f)

AUTHORIZED_VERSIONS = set(workbook_version_config["authorized_workbook_versions"])


# DESCRIPTION
# This checks if the uploaded workbook version is valid.
def validate_workbook_version(ir):
    version_range = get_range_by_name(ir, "version")
    errors = []

    for index, version in enumerate(version_range["values"]):
        if version not in AUTHORIZED_VERSIONS:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    version_range,
                    index,
                    get_message("check_workbook_version").format(version),
                )
            )

    if errors:
        raise ValidationError(errors)
