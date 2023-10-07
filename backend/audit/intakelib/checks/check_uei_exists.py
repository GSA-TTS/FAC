from django.core.exceptions import ValidationError
import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name
) 
from .util import (
    list_contains_non_null_values,
    get_message,
    build_range_error_tuple
    )

logger = logging.getLogger(__name__)

def uei_exists(ir):
    uei_range = get_range_by_name(ir, "auditee_uei")
    if (uei_range 
        and ("values" in uei_range)
        and list_contains_non_null_values(uei_range["values"])
        ):
        pass
    else:
        logger.info("Did not find a UEI.")
        return build_range_error_tuple(ir, 
                                       uei_range, 
                                       "auditee_uei", 
                                       get_message("check_uei_exists"))
