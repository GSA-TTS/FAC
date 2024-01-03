import logging

from django.conf import settings
from audit.intakelib.common import safe_int_conversion
from ..checks.check_cluster_total import NOT_APPLICABLE

logger = logging.getLogger(__name__)


# DESCRIPTION
# Convert end of period loan balance to integers when applicable
def convert_loan_balance_to_integers_or_na(ir):
    xform_ir = safe_int_conversion(
        ir, "loan_balance_at_audit_period_end", {NOT_APPLICABLE, settings.GSA_MIGRATION}
    )
    return xform_ir
