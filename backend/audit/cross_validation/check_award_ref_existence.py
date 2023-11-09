from audit.fixtures.excel import (
    FEDERAL_AWARDS_TEMPLATE_DEFINITION,
)
from .errors import (
    err_missing_award_reference,
)
from django.conf import settings
import json

TEMPLATE_DEFINITION_PATH = (
    settings.XLSX_TEMPLATE_JSON_DIR / FEDERAL_AWARDS_TEMPLATE_DEFINITION
)
FEDERAL_AWARDS_TEMPLATE = json.loads(
    TEMPLATE_DEFINITION_PATH.read_text(encoding="utf-8")
)


def check_award_ref_existence(sac_dict, *_args, **_kwargs):
    """
    Check that all awards have a reference code.
    """
    first_row = FEDERAL_AWARDS_TEMPLATE["title_row"]
    all_sections = sac_dict.get("sf_sac_sections", {})
    federal_awards_section = all_sections.get("federal_awards") or {}
    federal_awards = federal_awards_section.get("federal_awards", [])
    missing_refs = []
    errors = []
    for index, award in enumerate(federal_awards):
        if (
            "award_reference" not in award
        ):  # When award_reference exists the schema ensures it is not empty and has the correct shape
            missing_refs.append(first_row + index + 1)

    for row_num in missing_refs:
        errors.append({"error": err_missing_award_reference(row_num)})

    return errors
