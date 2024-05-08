import logging

from django.forms import ValidationError
from audit.intakelib.intermediate_representation import get_range_by_name
from audit.intakelib.common import (
    get_message,
    build_range_error_tuple,
)
from django.conf import settings

logger = logging.getLogger(__name__)


# `GSA_MIGRATION` is a default value assigned to any required fields
# that are missing, ensuring validation during the data migration process.
# See Ticket https://github.com/GSA-TTS/FAC/issues/2912.
# This function is to ensure the `GSA_MIGRATION` keyword is only used
# in the context of data migration.
def check_for_gsa_migration_keyword(ir):
    """Returns errors when required fields contain the `GSA_MIGRATION` keyword."""

    range_names = [
        "auditee_uei",
        "three_digit_extension",
        "additional_award_identification",
        "state_cluster_name",
        "other_cluster_name",
        "cluster_name",
        "loan_balance_at_audit_period_end",
        "passthrough_name",
        "passthrough_identifying_number",
        "contains_chart_or_table",
        "is_minimis_rate_used",
        "compliance_requirement",
        "auditee_zip",
        "auditor_zip",
    ]

    for range_name in range_names:
        range_data = get_range_by_name(ir, range_name)
        if (
            range_data
            and ("values" in range_data)
            and (settings.GSA_MIGRATION in range_data["values"])
        ):
            raise ValidationError(
                build_range_error_tuple(
                    ir,
                    range_data,
                    range_name,
                    get_message("check_gsa_migration_keyword"),
                )
            )
