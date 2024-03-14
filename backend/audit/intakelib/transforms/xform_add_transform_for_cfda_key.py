import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
)

logger = logging.getLogger(__name__)


def generate_cfda_keys(ir):
    cfda_keys = []
    federal_agency_prefixes = get_range_by_name(ir, "federal_agency_prefix")
    three_digit_extensions = get_range_by_name(ir, "three_digit_extension")
    for prefix, extension in zip(
        federal_agency_prefixes["values"], three_digit_extensions["values"]
    ):
        cfda_keys.append(f"{prefix}.{extension}" if prefix and extension else "")

    xform_ir = replace_range_by_name(ir, "cfda_key", cfda_keys)

    return xform_ir
