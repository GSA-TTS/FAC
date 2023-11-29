from audit.fixtures.excel import FORM_SECTIONS


from census_historical_migration.workbooklib.notes_to_sefa import generate_notes_to_sefa
from census_historical_migration.workbooklib.federal_awards import (
    generate_federal_awards,
)
from census_historical_migration.workbooklib.findings import generate_findings
from census_historical_migration.workbooklib.findings_text import generate_findings_text
from census_historical_migration.workbooklib.corrective_action_plan import (
    generate_corrective_action_plan,
)
from census_historical_migration.workbooklib.additional_ueis import (
    generate_additional_ueis,
)
from census_historical_migration.workbooklib.additional_eins import (
    generate_additional_eins,
)
from census_historical_migration.workbooklib.secondary_auditors import (
    generate_secondary_auditors,
)


sections_to_handlers = {
    FORM_SECTIONS.ADDITIONAL_EINS: generate_additional_eins,
    FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    FORM_SECTIONS.ADDITIONAL_UEIS: generate_additional_ueis,
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: generate_corrective_action_plan,
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: generate_federal_awards,
    FORM_SECTIONS.FINDINGS_TEXT: generate_findings_text,
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: generate_findings,
    FORM_SECTIONS.NOTES_TO_SEFA: generate_notes_to_sefa,
    FORM_SECTIONS.SECONDARY_AUDITORS: generate_secondary_auditors,
}
