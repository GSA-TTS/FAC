import logging

from audit.intakelib.checks.util import safe_int_conversion

logger = logging.getLogger(__name__)


# DESCRIPTION
# convert total amount expended to integers
def convert_total_amount_expended_to_integers(ir):
    xform_ir = safe_int_conversion(ir, "total_amount_expended")
    return xform_ir
