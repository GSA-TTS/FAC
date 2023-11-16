from audit.fixtures.excel import FORM_SECTIONS


# from .notes_to_sefa import generate_notes_to_sefa
from .federal_awards import (
    generate_federal_awards,
)

# from .findings import generate_findings
# from .findings_text import generate_findings_text
# from .corrective_action_plan import (
#     generate_corrective_action_plan,
# )
# from .additional_ueis import (
#     generate_additional_ueis,
# )
# from .additional_eins import (
#     generate_additional_eins,
# )
# from .secondary_auditors import (
#     generate_secondary_auditors,
# )


sections_to_handlers = {
    # FORM_SECTIONS.ADDITIONAL_EINS: generate_additional_eins,
    # FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    # FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    # FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: generate_corrective_action_plan,
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: generate_federal_awards,
    # FORM_SECTIONS.FINDINGS_TEXT: generate_findings_text,
    # FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: generate_findings,
    # FORM_SECTIONS.NOTES_TO_SEFA: generate_notes_to_sefa,
    # FORM_SECTIONS.SECONDARY_AUDITORS: generate_secondary_auditors,
}
