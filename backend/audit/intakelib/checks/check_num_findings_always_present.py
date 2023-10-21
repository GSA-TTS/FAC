import logging
from .util import get_missing_value_errors

logger = logging.getLogger(__name__)


def num_findings_always_present(ir):
    """The number of audit findings should always be present"""
    return get_missing_value_errors(
        ir, "number_of_audit_findings", "check_num_findings_always_present"
    )
