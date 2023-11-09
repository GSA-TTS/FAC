from audit.fixtures.excel import FORM_SECTIONS

import os


templates_root = "schemas/output/excel/xlsx/"
sections_to_template_files = {
    FORM_SECTIONS.ADDITIONAL_UEIS: "additional-ueis-workbook.xlsx",
    FORM_SECTIONS.ADDITIONAL_EINS: "additional-eins-workbook.xlsx",
    FORM_SECTIONS.FINDINGS_TEXT: "audit-findings-text-workbook.xlsx",
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: "corrective-action-plan-workbook.xlsx",
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: "federal-awards-audit-findings-workbook.xlsx",
    FORM_SECTIONS.FEDERAL_AWARDS_EXPENDED: "federal-awards-workbook.xlsx",
    FORM_SECTIONS.NOTES_TO_SEFA: "notes-to-sefa-workbook.xlsx",
    FORM_SECTIONS.SECONDARY_AUDITORS: "secondary-auditors-workbook.xlsx",
}

sections_to_template_paths = {}
for k, v in sections_to_template_files.items():
    sections_to_template_paths[k] = os.path.join(templates_root, v)
