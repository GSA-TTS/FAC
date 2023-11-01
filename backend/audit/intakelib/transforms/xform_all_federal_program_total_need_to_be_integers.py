import logging
from audit.intakelib.common import safe_int_conversion

logger = logging.getLogger(__name__)


# DESCRIPTION
# Convert all federal program totals to integers
def convert_federal_program_total_to_integers(ir):
    xform_ir = safe_int_conversion(ir, "federal_program_total")
    return xform_ir
