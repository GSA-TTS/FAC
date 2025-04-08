from audit.cross_validation.naming import NC, SECTION_NAMES as SN
from audit.fixtures.excel import FORM_SECTIONS
from audit.models.constants import EventType
from config.settings import STATIC_SITE_URL
from django.urls import reverse
from datetime import datetime

instructions_base_url = STATIC_SITE_URL + "resources/workbooks/"
workbook_base_url = STATIC_SITE_URL + "assets/workbooks/"


def create_upload_context(report_id):
    return {
        "federal-awards": {
            "view_id": "federal-awards",
            "view_name": "Federal awards",
            "instructions": "Enter the federal awards you received in the last audit year using the provided worksheet.",
            "DB_id": SN[NC.FEDERAL_AWARDS].snake_case,
            "instructions_url": instructions_base_url + "federal-awards/",
            "workbook_url": workbook_base_url + "federal-awards-workbook.xlsx",
            # below URL handled as a special case because of inconsistent name usage in audit/urls.py and audit/cross_validation/naming.py
            "existing_workbook_url": reverse(
                f"audit:{SN[NC.FEDERAL_AWARDS].camel_case}", args=[report_id]
            ),
        },
        "notes-to-sefa": {
            "view_id": "notes-to-sefa",
            "view_name": "Notes to SEFA",
            "instructions": "Enter the notes on the Schedule of Expenditures of Federal Awards (SEFA) using the provided worksheet.",
            "DB_id": SN[NC.NOTES_TO_SEFA].snake_case,
            "instructions_url": instructions_base_url + "notes-to-sefa/",
            "workbook_url": workbook_base_url + "notes-to-sefa-workbook.xlsx",
            "existing_workbook_url": reverse(
                f"audit:{SN[NC.NOTES_TO_SEFA].camel_case}", args=[report_id]
            ),
        },
        "audit-findings": {
            "view_id": "audit-findings",
            "view_name": "Audit findings",
            "instructions": "Enter the audit findings for your federal awards using the provided worksheet.",
            "DB_id": SN[NC.FINDINGS_UNIFORM_GUIDANCE].snake_case,
            "instructions_url": instructions_base_url
            + "federal-awards-audit-findings/",
            "no_findings_disclaimer": True,
            "workbook_url": workbook_base_url
            + "federal-awards-audit-findings-workbook.xlsx",
            "existing_workbook_url": reverse(
                f"audit:{SN[NC.FINDINGS_UNIFORM_GUIDANCE].camel_case}",
                args=[report_id],
            ),
            "remove_existing_workbook": reverse(
                f"report_submission:delete-{SN[NC.FINDINGS_UNIFORM_GUIDANCE].url_tail}",
                args=[report_id],
            ),
        },
        "audit-findings-text": {
            "view_id": "audit-findings-text",
            "view_name": "Audit findings text",
            "instructions": "Enter the text for your audit findings using the provided worksheet.",
            "DB_id": SN[NC.FINDINGS_TEXT].snake_case,
            "instructions_url": instructions_base_url
            + "federal-awards-audit-findings-text/",
            "no_findings_disclaimer": True,
            "workbook_url": workbook_base_url + "audit-findings-text-workbook.xlsx",
            "existing_workbook_url": reverse(
                f"audit:{SN[NC.FINDINGS_TEXT].camel_case}", args=[report_id]
            ),
            "remove_existing_workbook": reverse(
                f"report_submission:delete-{SN[NC.FINDINGS_TEXT].url_tail}",
                args=[report_id],
            ),
        },
        "cap": {
            "view_id": "cap",
            "view_name": "Corrective Action Plan (CAP)",
            "instructions": "Enter your CAP text using the provided worksheet.",
            "DB_id": SN[NC.CORRECTIVE_ACTION_PLAN].snake_case,
            "instructions_url": instructions_base_url + "corrective-action-plan/",
            "no_findings_disclaimer": True,
            "workbook_url": workbook_base_url + "corrective-action-plan-workbook.xlsx",
            "existing_workbook_url": reverse(
                f"audit:{SN[NC.CORRECTIVE_ACTION_PLAN].camel_case}",
                args=[report_id],
            ),
            "remove_existing_workbook": reverse(
                f"report_submission:delete-{SN[NC.CORRECTIVE_ACTION_PLAN].url_tail.upper()}",
                args=[report_id],
            ),
        },
        "additional-ueis": {
            "view_id": "additional-ueis",
            "view_name": "Additional UEIs",
            "instructions": "Enter any additional UEIs using the provided worksheet.",
            "DB_id": SN[NC.ADDITIONAL_UEIS].snake_case,
            "instructions_url": instructions_base_url + "additional-ueis-workbook/",
            "workbook_url": workbook_base_url + "additional-ueis-workbook.xlsx",
            "existing_workbook_url": reverse("audit:AdditionalUeis", args=[report_id]),
            "remove_existing_workbook": reverse(
                f"report_submission:delete-{SN[NC.ADDITIONAL_UEIS].url_tail}",
                args=[report_id],
            ),
        },
        "secondary-auditors": {
            "view_id": "secondary-auditors",
            "view_name": "Secondary auditors",
            "instructions": "Enter any additional auditors using the provided worksheet.",
            "DB_id": SN[NC.SECONDARY_AUDITORS].snake_case,
            "instructions_url": instructions_base_url + "secondary-auditors-workbook/",
            "workbook_url": workbook_base_url + "secondary-auditors-workbook.xlsx",
            # below URLs handled as a special case because of inconsistent name usage in audit/urls.py and audit/cross_validation/naming.py
            "existing_workbook_url": reverse(
                f"audit:{SN[NC.SECONDARY_AUDITORS].camel_case}", args=[report_id]
            ),
            "remove_existing_workbook": reverse(
                f"report_submission:delete-{SN[NC.SECONDARY_AUDITORS].url_tail}",
                args=[report_id],
            ),
        },
        "additional-eins": {
            "view_id": "additional-eins",
            "view_name": "Additional EINs",
            "instructions": "Enter any additional EINs using the provided worksheet.",
            "DB_id": SN[NC.ADDITIONAL_EINS].snake_case,
            "instructions_url": instructions_base_url + "additional-eins-workbook/",
            "workbook_url": workbook_base_url + "additional-eins-workbook.xlsx",
            # below URLs handled as a special case because of inconsistent name usage in audit/urls.py and audit/cross_validation/naming.py
            "existing_workbook_url": reverse("audit:AdditionalEins", args=[report_id]),
            "remove_existing_workbook": reverse(
                f"report_submission:delete-{SN[NC.ADDITIONAL_EINS].url_tail}",
                args=[report_id],
            ),
        },
    }


def create_delete_context():
    return {
        "delete-audit-findings": {
            "view_id": "delete-audit-findings",
            "section_name": SN[NC.FINDINGS_UNIFORM_GUIDANCE].friendly_title,
            "field_name": SN[NC.FINDINGS_UNIFORM_GUIDANCE].snake_case,
            "form_section": FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE,
            "event_type": EventType.FINDINGS_UNIFORM_GUIDANCE_DELETED,
        },
        "delete-audit-findings-text": {
            "view_id": "delete-audit-findings-text",
            "section_name": SN[NC.FINDINGS_TEXT].friendly_title,
            "field_name": SN[NC.FINDINGS_TEXT].snake_case,
            "form_section": FORM_SECTIONS.FINDINGS_TEXT,
            "event_type": EventType.FEDERAL_AWARDS_AUDIT_FINDINGS_TEXT_DELETED,
        },
        "delete-cap": {
            "view_id": "delete-cap",
            "section_name": SN[NC.CORRECTIVE_ACTION_PLAN].friendly_title,
            "field_name": SN[NC.CORRECTIVE_ACTION_PLAN].snake_case,
            "form_section": FORM_SECTIONS.CORRECTIVE_ACTION_PLAN,
            "event_type": EventType.CORRECTIVE_ACTION_PLAN_DELETED,
        },
        "delete-additional-ueis": {
            "view_id": "delete-additional-ueis",
            "section_name": SN[NC.ADDITIONAL_UEIS].friendly_title,
            "field_name": SN[NC.ADDITIONAL_UEIS].snake_case,
            "form_section": FORM_SECTIONS.ADDITIONAL_UEIS,
            "event_type": EventType.ADDITIONAL_UEIS_DELETED,
        },
        "delete-secondary-auditors": {
            "view_id": "delete-secondary-auditors",
            "section_name": SN[NC.SECONDARY_AUDITORS].friendly_title,
            "field_name": SN[NC.SECONDARY_AUDITORS].snake_case,
            "form_section": FORM_SECTIONS.SECONDARY_AUDITORS,
            "event_type": EventType.SECONDARY_AUDITORS_DELETED,
        },
        "delete-additional-eins": {
            "view_id": "delete-additional-eins",
            "section_name": SN[NC.ADDITIONAL_EINS].friendly_title,
            "field_name": SN[NC.ADDITIONAL_EINS].snake_case,
            "form_section": FORM_SECTIONS.ADDITIONAL_EINS,
            "event_type": EventType.ADDITIONAL_EINS_DELETED,
        },
    }


def parse_slashed_date(date_str):
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return date_str


def parse_hyphened_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%m/%d/%Y")
    except ValueError:
        return date_str
