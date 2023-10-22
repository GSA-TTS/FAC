from django.core.exceptions import ValidationError
from openpyxl import load_workbook
from audit.intakelib.intermediate_representation import (
    extract_workbook_as_ir,
)
from .util import (
    get_names_of_all_ranges
)
from audit.cross_validation.naming import SECTION_NAMES, find_section_by_name
from audit.fixtures.excel import FORM_SECTIONS
from audit.fixtures.excel import (
    ADDITIONAL_UEIS_TEMPLATE,
    NOTES_TO_SEFA_TEMPLATE,
    ADDITIONAL_EINS_TEMPLATE,
    FEDERAL_AWARDS_TEMPLATE,
    FINDINGS_TEXT_TEMPLATE,
    CORRECTIVE_ACTION_PLAN_TEMPLATE,
    FINDINGS_UNIFORM_GUIDANCE_TEMPLATE,
    SECONDARY_AUDITORS_TEMPLATE
)

# It would be nice if these mappings were part of names.py. 
# However, this is almost like configuration data. That said,
# I need an easy way to map from a section name to the path to the template.
map_section_to_workbook = {
        FORM_SECTIONS.ADDITIONAL_UEIS: ADDITIONAL_UEIS_TEMPLATE,
        FORM_SECTIONS.NOTES_TO_SEFA: NOTES_TO_SEFA_TEMPLATE,
        FORM_SECTIONS.ADDITIONAL_EINS: ADDITIONAL_EINS_TEMPLATE,
        FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: FEDERAL_AWARDS_TEMPLATE,
        FORM_SECTIONS.FINDINGS_TEXT: FINDINGS_TEXT_TEMPLATE,
        FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: CORRECTIVE_ACTION_PLAN_TEMPLATE,
        FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: FINDINGS_UNIFORM_GUIDANCE_TEMPLATE,
        FORM_SECTIONS.SECONDARY_AUDITORS: SECONDARY_AUDITORS_TEMPLATE
}

# DESCRIPTION
# Some workbooks come in mangled. We lose named ranges.
# This becomes a problem for some later checks. So, as an early check, we should:
# 
# 1. Load the template.
# 2. Extract the named ranges from the template
# 3. Compare the template named ranges to the IR
# 
# If we're missing anything, we need to bail immediately. They have mangled the workbook.
# We should not accept the submission.
def has_all_the_named_ranges(section_name):
    def _given_the_ir(ir):
        template = load_workbook(map_section_to_workbook[section_name], data_only=True)
        template_ir = extract_workbook_as_ir(template)
        template_names = get_names_of_all_ranges(template_ir)
        their_names = get_names_of_all_ranges(ir)
        for tname in template_names:
            if tname not in their_names:
                raise ValidationError(
                    (
                        "Workbook",
                        "",
                        section_name,
                        {"text": f"This FAC workbook is missing the range <b>{tname}</b>. Please download a fresh template and transfer your data", "link": "Intake checks: no link defined"},

                    )
                )
    return _given_the_ir
