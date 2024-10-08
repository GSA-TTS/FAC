from audit.fixtures.excel import FORM_SECTIONS


from ..workbooklib.notes_to_sefa import generate_notes_to_sefa
from ..workbooklib.federal_awards import (
    generate_federal_awards,
)
from ..workbooklib.findings import generate_findings
from ..workbooklib.findings_text import generate_findings_text
from ..workbooklib.corrective_action_plan import (
    generate_corrective_action_plan,
)
from ..workbooklib.additional_ueis import (
    generate_additional_ueis,
)
from ..workbooklib.additional_eins import (
    generate_additional_eins,
)
from ..workbooklib.secondary_auditors import (
    generate_secondary_auditors,
)


sections_to_handlers = {
    FORM_SECTIONS.ADDITIONAL_EINS: generate_additional_eins,
    FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: generate_corrective_action_plan,
    FORM_SECTIONS.FEDERAL_AWARDS: generate_federal_awards,
    FORM_SECTIONS.FINDINGS_TEXT: generate_findings_text,
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: generate_findings,
    FORM_SECTIONS.NOTES_TO_SEFA: generate_notes_to_sefa,
    FORM_SECTIONS.SECONDARY_AUDITORS: generate_secondary_auditors,
}
