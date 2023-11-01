import logging

from audit.intakelib.common import safe_int_conversion

logger = logging.getLogger(__name__)


# DESCRIPTION
# Convert all cluster totals to integers
def convert_cluster_total_to_integers(ir):
    xform_ir = safe_int_conversion(ir, "cluster_total")
    return xform_ir
