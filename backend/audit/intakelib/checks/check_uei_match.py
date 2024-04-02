import logging
from audit.intakelib.intermediate_representation import get_range_by_name
from audit.intakelib.common import (
    get_message,
    build_range_error_tuple,
)

logger = logging.getLogger(__name__)


def verify_auditee_uei_match(ir, auditee_uei):
    """Verify that the auditee UEIs on the coversheet and in General Information section match."""
    uei_range = get_range_by_name(ir, "auditee_uei")
    uei_value = uei_range.get("values")
    for uei in uei_value:
        if auditee_uei and auditee_uei != uei:
            logger.info(f"UEI {auditee_uei} does not match {uei}.")
            return build_range_error_tuple(
                ir, uei_range, "auditee_uei", get_message("check_uei_match")
            )
