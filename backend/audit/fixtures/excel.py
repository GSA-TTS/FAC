"""
Fixtures for use with Excel spreadsheet handling.
"""
from collections import namedtuple
from django.conf import settings

UNKNOWN_WORKBOOK = "unknown_workbook"
SHEETS_DIR = settings.XLSX_TEMPLATE_SHEET_DIR
TESTFILES_DIR = settings.DATA_FIXTURES / "audit" / "excel_schema_test_files"

ADDITIONAL_UEIS_TEMPLATE = SHEETS_DIR / "additional-ueis-workbook.xlsx"
FEDERAL_AWARDS_TEMPLATE = SHEETS_DIR / "federal-awards-workbook.xlsx"
FINDINGS_TEXT_TEMPLATE = SHEETS_DIR / "audit-findings-text-workbook.xlsx"
CORRECTIVE_ACTION_PLAN_TEMPLATE = SHEETS_DIR / "corrective-action-plan-workbook.xlsx"
FINDINGS_UNIFORM_GUIDANCE_TEMPLATE = (
    SHEETS_DIR / "federal-awards-audit-findings-workbook.xlsx"
)
SECONDARY_AUDITORS_TEMPLATE = SHEETS_DIR / "secondary-auditors-workbook.xlsx"
NOTES_TO_SEFA_TEMPLATE = SHEETS_DIR / "notes-to-sefa-workbook.xlsx"

ADDITIONAL_UEIS_TEMPLATE_DEFINITION = "additional-ueis-workbook.json"
FEDERAL_AWARDS_TEMPLATE_DEFINITION = "federal-awards-workbook.json"
CORRECTIVE_ACTION_TEMPLATE_DEFINITION = "corrective-action-plan-workbook.json"
FINDINGS_UNIFORM_TEMPLATE_DEFINITION = "federal-awards-audit-findings-workbook.json"
FINDINGS_TEXT_TEMPLATE_DEFINITION = "audit-findings-text-workbook.json"
SECONDARY_AUDITORS_TEMPLATE_DEFINITION = "secondary-auditors-workbook.json"
NOTES_TO_SEFA_TEMPLATE_DEFINITION = "notes-to-sefa-workbook.json"

ADDITIONAL_UEIS_TEST_FILE = TESTFILES_DIR / "additional-ueis-pass-01.json"
FEDERAL_AWARDS_TEST_FILE = TESTFILES_DIR / "federal-awards-pass-01.json"
CORRECTIVE_ACTION_PLAN_TEST_FILE = TESTFILES_DIR / "corrective-action-plan-pass-01.json"
FINDINGS_TEXT_TEST_FILE = TESTFILES_DIR / "audit-findings-text-pass-01.json"
FINDINGS_UNIFORM_GUIDANCE_TEST_FILE = (
    TESTFILES_DIR / "federal-awards-audit-findings-pass-01.json"
)
SECONDARY_AUDITORS_TEST_FILE = TESTFILES_DIR / "secondary-auditors-pass-01.json"
NOTES_TO_SEFA_TEST_FILE = TESTFILES_DIR / "notes-to-sefa-pass-01.json"

ADDITIONAL_UEIS_ENTRY_FIXTURES = (
    settings.AUDIT_TEST_DATA_ENTRY_DIR / "additional-ueis-entries.json"
)
CORRECTIVE_ACTION_PLAN_ENTRY_FIXTURES = (
    settings.AUDIT_TEST_DATA_ENTRY_DIR / "corrective-action-plan-entries.json"
)
FINDINGS_TEXT_ENTRY_FIXTURES = (
    settings.AUDIT_TEST_DATA_ENTRY_DIR / "audit-findings-text-entries.json"
)
FINDINGS_UNIFORM_GUIDANCE_ENTRY_FIXTURES = (
    settings.AUDIT_TEST_DATA_ENTRY_DIR / "federal-awards-audit-findings-entries.json"
)
FEDERAL_AWARDS_ENTRY_FIXTURES = (
    settings.AUDIT_TEST_DATA_ENTRY_DIR / "federal-awards-entries.json"
)
SECONDARY_AUDITORS_ENTRY_FIXTURES = (
    settings.AUDIT_TEST_DATA_ENTRY_DIR / "secondary-auditors-entries.json"
)
NOTES_TO_SEFA_ENTRY_FIXTURES = (
    settings.AUDIT_TEST_DATA_ENTRY_DIR / "notes-to-sefa-entries.json"
)
SIMPLE_CASES_TEST_FILE = settings.AUDIT_TEST_DATA_ENTRY_DIR / "simple-cases.json"

# Make FORM_SECTIONS convenient to both iterate over and access by field name:
FormSections = namedtuple(
    "FormSections",
    (
        "CORRECTIVE_ACTION_PLAN",
        "FEDERAL_AWARDS_EXPENDED",
        "FINDINGS_TEXT",
        "FINDINGS_UNIFORM_GUIDANCE",
        "ADDITIONAL_UEIS",
        "SECONDARY_AUDITORS",
        "NOTES_TO_SEFA",
    ),
)
# Note: we turn these into hyphenated lowercase for URLs, e.g. federal-awards-expended
FORM_SECTIONS = FormSections(
    CORRECTIVE_ACTION_PLAN="CorrectiveActionPlan",
    FEDERAL_AWARDS_EXPENDED="FederalAwardsExpended",
    FINDINGS_TEXT="FindingsText",
    FINDINGS_UNIFORM_GUIDANCE="FindingsUniformGuidance",
    ADDITIONAL_UEIS="AdditionalUeis",
    SECONDARY_AUDITORS="SecondaryAuditors",
    NOTES_TO_SEFA="NotesToSefa",
)

# FIXME MSHD: We should consolidate SectionNames with the above FormSections
SectionNames = namedtuple(
    "SectionNames",
    (
        "ADDITIONAL_UEIS",
        "AUDIT_FINDINGS_TEXT",
        "CORRECTIVE_ACTION_PLAN",
        "FEDERAL_AWARDS",
        "FEDERAL_AWARDS_AUDIT_FINDINGS",
        "NOTES_TO_SEFA",
        "SECONDARY_AUDITORS",
    ),
)
SECTION_NAMES = SectionNames(
    ADDITIONAL_UEIS="Additional UEIs",
    AUDIT_FINDINGS_TEXT="Audit Findings Text",
    CORRECTIVE_ACTION_PLAN="Corrective Action Plan",
    FEDERAL_AWARDS="Federal Awards",
    FEDERAL_AWARDS_AUDIT_FINDINGS="Federal Awards Audit Findings",
    NOTES_TO_SEFA="Notes to SEFA",
    SECONDARY_AUDITORS="Secondary Auditors",
)
