import json
import logging
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from django.conf import settings
from audit.intakelib.intermediate_representation import get_range_by_name
from audit.intakelib.common import (
    get_message,
    build_range_error_tuple,
)

logger = logging.getLogger(__name__)


def verify_auditee_uei_schema(ir):
    """Verify that the auditee UEI schema is valid."""
    uei_range = get_range_by_name(ir, "auditee_uei")
    uei_value = uei_range.get("values")
    with open(f"{settings.OUTPUT_BASE_DIR}/UeiSchema.json") as file:
        schema = json.load(file)
    for index, uei in enumerate(uei_value):
        try:
            data = {"uei": uei}
            validate(instance=data, schema=schema)
        except ValidationError as e:
            logger.info(f"Error validating auditee UEI schema: {e}")
            return build_range_error_tuple(
                ir, uei_range, "auditee_uei", get_message("check_uei_schema")
            )
