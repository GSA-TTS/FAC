import logging

from django.core.exceptions import ValidationError

from ..intermediate_representation import get_range_by_name
from ..common import get_message, build_cell_error_tuple


logger = logging.getLogger(__name__)


def alns_are_valid(ir):
    """
    Raises an error if an ALN (prefix.extension) is not found in the column of
    valid ALNs provided in the FederalPrograms sheet.
    """
    valid_alns = get_range_by_name(ir, "aln_lookup").get("values")
    prefix_range = get_range_by_name(ir, "federal_agency_prefix")
    prefixes = prefix_range.get("values")
    extensions = get_range_by_name(ir, "three_digit_extension").get("values")
    errors = []

    for index in range(max(len(prefixes), len(extensions))):
        prefix = prefixes[index]
        extension = extensions[index]
        aln = f"{prefix}.{extension}"

        if aln not in valid_alns:
            errors.append(
                build_cell_error_tuple(
                    ir,
                    prefix_range,
                    index,
                    get_message("check_aln_invalid").format(aln),
                )
            )

    if errors:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)
