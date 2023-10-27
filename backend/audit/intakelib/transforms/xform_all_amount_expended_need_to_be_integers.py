import logging
from audit.intakelib.checks.util import safe_int_conversion

logger = logging.getLogger(__name__)


# DESCRIPTION
# Convert all amount expended to integers
def convert_amount_expended_to_integers(ir):
    xform_ir = safe_int_conversion(ir, "amount_expended")
    return xform_ir
