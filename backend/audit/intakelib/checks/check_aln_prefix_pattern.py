import json
import logging
import re

from django.conf import settings
from django.core.exceptions import ValidationError

from audit.fixtures.excel import FEDERAL_AWARDS_JSONSCHEMA
from ..common import get_message, build_cell_error_tuple
from ..intermediate_representation import get_range_by_name


logger = logging.getLogger(__name__)


# DESCRIPTION
# The ALN prefix represents a two-digit number ##
# TESTED BY has_bad_aln_prefix.xlsx
def aln_agency_prefix(ir):
    json_input = json.loads(FEDERAL_AWARDS_JSONSCHEMA.read_text(encoding="utf-8"))
    print("#########")
    print(json_input["filename"])
    print(json_input["sheets"][3]["name"])
    print("#########")
    prefixes = get_range_by_name(ir, "federal_agency_prefix")
    errors = []
    for index, prefix in enumerate(prefixes["values"]):
        if not re.match(settings.REGEX_ALN_PREFIX, str(prefix)):
            errors.append(
                build_cell_error_tuple(
                    ir,
                    prefixes,
                    index,
                    get_message("check_aln_prefix_invalid"),
                )
            )

    if len(errors) > 0:
        logger.info("Raising a validation error.")
        raise ValidationError(errors)
