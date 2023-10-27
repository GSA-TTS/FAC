import logging
from audit.intakelib.checks.util import safe_int_conversion

logger = logging.getLogger(__name__)


# DESCRIPTION
# Convert all number_of_audit_findings to integers
def convert_number_of_findings_to_integers(ir):
    xform_ir = safe_int_conversion(ir, "number_of_audit_findings")
    return xform_ir
