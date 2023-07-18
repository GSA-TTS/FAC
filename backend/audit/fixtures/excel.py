"""
Fixtures for use with Excel spreadsheet handling.
"""
from collections import namedtuple
from django.conf import settings

SHEETS_DIR = settings.XLSX_TEMPLATE_SHEET_DIR
TESTFILES_DIR = settings.DATA_FIXTURES / "audit" / "excel_schema_test_files"

ADDITIONAL_UEIS_TEMPLATE = SHEETS_DIR / "additional-ueis-template.xlsx"
FEDERAL_AWARDS_TEMPLATE = SHEETS_DIR / "federal-awards-expended-template.xlsx"
FINDINGS_TEXT_TEMPLATE = SHEETS_DIR / "findings-text-template.xlsx"
CORRECTIVE_ACTION_PLAN_TEMPLATE = SHEETS_DIR / "corrective-action-plan-template.xlsx"
FINDINGS_UNIFORM_GUIDANCE_TEMPLATE = (
    SHEETS_DIR / "findings-uniform-guidance-template.xlsx"
)
NOTES_TO_SEFA_TEMPLATE = SHEETS_DIR / "notes-to-sefa-template.xlsx"

ADDITIONAL_UEIS_TEMPLATE_DEFINITION = "additional-ueis-template.json"
FEDERAL_AWARDS_TEMPLATE_DEFINITION = "federal-awards-expended-template.json"
CORRECTIVE_ACTION_TEMPLATE_DEFINITION = "corrective-action-plan-template.json"
FINDINGS_UNIFORM_TEMPLATE_DEFINITION = "findings-uniform-guidance-template.json"
FINDINGS_TEXT_TEMPLATE_DEFINITION = "findings-text-template.json"
NOTES_TO_SEFA_TEMPLATE_DEFINITION = "notes-to-sefa-template.json"

ADDITIONAL_UEIS_TEST_FILE = TESTFILES_DIR / "additional-ueis-pass-01.json"
FEDERAL_AWARDS_TEST_FILE = TESTFILES_DIR / "federalawards-pass-01.json"
CORRECTIVE_ACTION_PLAN_TEST_FILE = TESTFILES_DIR / "corrective-action-plan-pass-01.json"
FINDINGS_TEXT_TEST_FILE = TESTFILES_DIR / "findings-text-pass-01.json"
FINDINGS_UNIFORM_GUIDANCE_TEST_FILE = (
    TESTFILES_DIR / "findings-uniform-guidance-pass-01.json"
)
NOTES_TO_SEFA_TEST_FILE = TESTFILES_DIR / "notes-to-sefa-pass-01.json"

ADDITIONAL_UEIS_ENTRY_FIXTURES = (
    settings.AUDIT_TEST_DATA_ENTRY_DIR / "additional-ueis-entries.json"
)
CORRECTIVE_ACTION_PLAN_ENTRY_FIXTURES = (
    settings.AUDIT_TEST_DATA_ENTRY_DIR / "corrective-action-plan-entries.json"
)
FINDINGS_TEXT_ENTRY_FIXTURES = (
    settings.AUDIT_TEST_DATA_ENTRY_DIR / "findings-text-entries.json"
)
FINDINGS_UNIFORM_GUIDANCE_ENTRY_FIXTURES = (
    settings.AUDIT_TEST_DATA_ENTRY_DIR / "findings-uniform-guidance-entries.json"
)
FEDERAL_AWARDS_ENTRY_FIXTURES = (
    settings.AUDIT_TEST_DATA_ENTRY_DIR / "federal-awards-expended-entries.json"
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
    NOTES_TO_SEFA="NotesToSefa",
)
