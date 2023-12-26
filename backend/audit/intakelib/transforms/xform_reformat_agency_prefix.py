import logging
from audit.intakelib.intermediate_representation import (
    get_range_by_name,
    replace_range_by_name,
)

logger = logging.getLogger(__name__)


# Tested by has-aln-prefix-entered-as-numbers.xlsx
def reformat_federal_agency_prefix(ir):
    references = get_range_by_name(ir, "federal_agency_prefix")
    new_values = list(map(lambda v: v.split(".")[0] if v else v, references["values"]))
    new_ir = replace_range_by_name(ir, "federal_agency_prefix", new_values)
    return new_ir
