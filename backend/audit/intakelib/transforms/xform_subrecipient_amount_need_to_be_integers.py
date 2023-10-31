import logging
from audit.intakelib.checks.util import safe_int_conversion

logger = logging.getLogger(__name__)


# DESCRIPTION
# Convert all subrecipient_amount to integers
def convert_subrecipient_amount_to_integers(ir):
    xform_ir = safe_int_conversion(ir, "subrecipient_amount")
    return xform_ir
