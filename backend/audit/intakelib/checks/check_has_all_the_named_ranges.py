import json
from django.core.exceptions import ValidationError
from audit.intakelib.common import get_names_of_all_ranges
from audit.fixtures.excel import FORM_SECTIONS
from audit.fixtures.excel import (
    ADDITIONAL_UEIS_JSONSCHEMA,
    NOTES_TO_SEFA_JSONSCHEMA,
    ADDITIONAL_EINS_JSONSCHEMA,
    FEDERAL_AWARDS_JSONSCHEMA,
    FINDINGS_TEXT_JSONSCHEMA,
    CORRECTIVE_ACTION_PLAN_JSONSCHEMA,
    FINDINGS_UNIFORM_GUIDANCE_JSONSCHEMA,
    SECONDARY_AUDITORS_JSONSCHEMA,
)

# It would be nice if these mappings were part of names.py.
# However, this is almost like configuration data. That said,
# I need an easy way to map from a section name to the path to the template.
map_section_to_jsonschema = {
    FORM_SECTIONS.ADDITIONAL_UEIS: ADDITIONAL_UEIS_JSONSCHEMA,
    FORM_SECTIONS.NOTES_TO_SEFA: NOTES_TO_SEFA_JSONSCHEMA,
    FORM_SECTIONS.ADDITIONAL_EINS: ADDITIONAL_EINS_JSONSCHEMA,
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: FEDERAL_AWARDS_JSONSCHEMA,
    FORM_SECTIONS.FINDINGS_TEXT: FINDINGS_TEXT_JSONSCHEMA,
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: CORRECTIVE_ACTION_PLAN_JSONSCHEMA,
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: FINDINGS_UNIFORM_GUIDANCE_JSONSCHEMA,
    FORM_SECTIONS.SECONDARY_AUDITORS: SECONDARY_AUDITORS_JSONSCHEMA,
}


def json_nr_lookup(json_input, lookup_key):
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if k == lookup_key:
                yield v
            else:
                yield from json_nr_lookup(v, lookup_key)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from json_nr_lookup(item, lookup_key)


# DESCRIPTION
# Some workbooks come in mangled. We lose named ranges.
# This becomes a problem for some later checks. So, as an early check, we should:
#
# 1. Extract list of expected named ranges from our rendered jsonschema.
# 2. Compare the jsonschema named ranges to the IR
#
# If we're missing anything, we need to bail immediately. They have mangled the workbook.
# We should not accept the submission.
TEMPLATES = {}
for section in map_section_to_jsonschema:
    json_path = map_section_to_jsonschema[section]
    json_input = json.loads(json_path.read_text(encoding="utf-8"))

    TEMPLATES[section] = json_nr_lookup(json_input, "range_name")


def has_all_the_named_ranges(section_name):
    def _given_the_ir(ir):
        template_names = TEMPLATES[section_name]
        their_names = get_names_of_all_ranges(ir)
        for tname in template_names:
            if tname not in their_names:
                raise ValidationError(
                    (
                        "Workbook",
                        "",
                        section_name,
                        {
                            "text": f"This FAC workbook is missing the range <b>{tname}</b>. Please download a fresh template and transfer your data",
                            "link": "Intake checks: no link defined",
                        },
                    )
                )

    return _given_the_ir
