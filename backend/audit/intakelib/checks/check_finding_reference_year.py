import logging
from django.core.exceptions import ValidationError
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
)
from audit.intakelib.common import (
    get_message,
    build_cell_error_tuple,
)

from audit.context import get_sac_from_context
from audit.intakelib.common.util import get_range_start_row

logger = logging.getLogger(__name__)


# DESCRIPTION
# Finding references should be in 20##-### format where the first four
# digits match the audit_year.


def finding_reference_year(ir, is_gsa_migration=False):
    references = get_range_by_name(ir, "reference_number")
    range_start = int(get_range_start_row(references))
    errors = []
    sac = get_sac_from_context()

    if is_gsa_migration or sac and sac.general_information is None:
        # In real use cases, no report can be created if auditee_uei is missing, as it is a required field.
        # The condition sac.general_information is None can occur only in test cases
        # where general_information has been ignored purposefully (like in test_workbooks_should_pass.py).
        return
    elif sac is None:
        raise ValidationError(
            (
                "(O_o)",
                "",
                "Workbook Validation Failed",
                {
                    "text": "The workbook cannot be validated at the moment. Please contact the helpdesk for assistance.",
                    "link": "Intake checks: no link defined",
                },
            )
        )
    audit_date = sac.general_information["auditee_fiscal_period_end"]
    audit_year = int(audit_date.split("-")[0])
    for index, reference in enumerate(references["values"]):
        year = int(reference.split("-")[0])
        if audit_year != year:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    references,
                    index,
                    get_message("check_invalid_finding_reference_year").format(
                        reference, index + range_start, audit_year
                    ),
                )
            )

    if len(errors) > 0:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)
