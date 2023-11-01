import logging
from .util import invalid_y_or_n_entry
from audit.fixtures.excel import FORM_SECTIONS

logger = logging.getLogger(__name__)

map_yorn_field_ranges_to_workbook = {
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: [
        "is_guaranteed",
        "is_direct",
        "is_passed",
        "is_major",
    ],
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: [
        "modified_opinion",
        "other_matters",
        "material_weakness",
        "significant_deficiency",
        "other_findings",
        "questioned_costs",
        "repeat_prior_reference",
        "is_valid",
    ],
    # FIXME: MSHD - will add the sections below in follow up PRs.
    # FORM_SECTIONS.FINDINGS_TEXT:["contains_chart_or_table"],
    # FORM_SECTIONS.CORRECTIVE_ACTION_PLAN:["contains_chart_or_table"]
}


# check if any Y/N field is invalid
def has_invalid_yorn_field(section_name):
    def _invalid_yorn(ir):
        yorn_field_ranges = map_yorn_field_ranges_to_workbook[section_name]
        errors = []
        for range_name in yorn_field_ranges:
            errors.extend(
                invalid_y_or_n_entry(ir, range_name, "check_invalid_y_or_n_entry")
            )

        return errors

    return _invalid_yorn
