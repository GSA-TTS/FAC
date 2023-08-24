from typing import NamedTuple

# There's no way around it, we need a canonical source of the different versions of each
# name.
"""
    Starting point:

        "AdditionalUEIs": "additional_ueis",
        "AdditionalUEIs": "additional_ueis",
        "AuditInformation": "audit_information",
        "CorrectiveActionPlan": "corrective_action_plan",
        "FederalAwards": "federal_awards",
        "FindingsText": "findings_text",
        "FindingsUniformGuidance": "findings_uniform_guidance",
        "GeneralInformation": "general_information",
        "NotesToSefa": "notes_to_sefa",
        "TribalDataConsent": "tribal_data_consent",
"""


class SectionBabelFish(NamedTuple):
    """
    NamedTuple to hold the various versions of section names.
    """

    all_caps: str  # Mostly used for workbooks.
    camel_case: str  # Mostly used in JSON Schemas.
    friendly: str  # The name we show to users.
    friendly_title: str  # The title on the submission progress page/form page.
    reverse_url: str  # Django value for finding the actual URL.
    snake_case: str  # Mostly used for the field names in SingleAuditChecklist.
    url_tail: str  # Hyphenated version of snake_case, mostly.
    workbook_number: int | None  # Our upload ordering of workbooks.


section_names = {
    "additional_eins": SectionBabelFish(
        **{
            "all_caps": "ADDITIONAL_EINS",
            "camel_case": "AdditionalEINs",
            "friendly": "Additional EINs",
            "friendly_title": "Additional EINs",
            "reverse_url": "report_submission:additional-eins",
            "snake_case": "additional_eins",
            "url_tail": "additional-eins",
            "workbook_number": 8,
        }
    ),
    "additional_ueis": SectionBabelFish(
        **{
            "all_caps": "ADDITIONAL_UEIS",
            "camel_case": "AdditionalUEIs",
            "friendly": "Additional UEIs",
            "friendly_title": "Additional UEIs",
            "reverse_url": "report_submission:additional-ueis",
            "snake_case": "additional_ueis",
            "url_tail": "additional-ueis",
            "workbook_number": 6,
        }
    ),
    "audit_information": SectionBabelFish(
        **{
            "all_caps": "AUDIT_INFORMATION",
            "camel_case": "AuditInformation",
            "friendly": "Audit Information",
            "friendly_title": "Audit Information form",
            "reverse_url": "audit:AuditInfoForm",
            "snake_case": "audit_information",
            "url_tail": "audit-information",
            "workbook_number": None,
        }
    ),
    "corrective_action_plan": SectionBabelFish(
        **{
            "all_caps": "CORRECTIVE_ACTION_PLAN",
            "camel_case": "CorrectiveActionPlan",
            "friendly": "Corrective Action Plan",
            "friendly_title": "Corrective Action Plan",
            "snake_case": "corrective_action_plan",
            "reverse_url": "report_submission:CAP",
            "url_tail": "cap",
            "workbook_number": 5,
        }
    ),
    "federal_awards": SectionBabelFish(
        **{
            "all_caps": "FEDERAL_AWARDS",
            "camel_case": "FederalAwards",
            "friendly": "Federal Awards",
            "friendly_title": "Federal Awards",
            "reverse_url": "report_submission:federal-awards",
            "snake_case": "federal_awards",
            "url_tail": "federal-awards",
            "workbook_number": 1,
        }
    ),
    "findings_text": SectionBabelFish(
        **{
            "all_caps": "FINDINGS_TEXT",
            "camel_case": "FindingsText",
            "friendly": "Federal Awards Audit Findings Text",
            "friendly_title": "Federal Awards Audit Findings Text",
            "reverse_url": "report_submission:audit-findings",
            "snake_case": "findings_text",
            "url_tail": "audit-findings",
            "workbook_number": 4,
        }
    ),
    "findings_uniform_guidance": SectionBabelFish(
        **{
            "all_caps": "FINDINGS_UNIFORM_GUIDANCE",
            "camel_case": "FindingsUniformGuidance",
            "friendly": "Findings Uniform Guidance",
            "friendly_title": "Federal Awards Audit Findings",
            "reverse_url": "report_submission:audit_findings",
            "snake_case": "findings_uniform_guidance",
            "url_tail": "audit-findings",
            "workbook_number": 3,
        }
    ),
    "general_information": SectionBabelFish(
        **{
            "all_caps": "GENERAL_INFORMATION",
            "camel_case": "GeneralInformation",
            "friendly": "General Information",
            "friendly_title": "General Information form",
            "reverse_url": "report_submission:general_information",
            "snake_case": "general_information",
            "url_tail": "general-information",
            "workbook_number": None,
        }
    ),
    "notes_to_sefa": SectionBabelFish(
        **{
            "all_caps": "NOTES_TO_SEFA",
            "camel_case": "NotesToSefa",
            "friendly": "Notes to SEFA",
            "friendly_title": "General Information form",
            "reverse_url": "report_submission:general_information",
            "snake_case": "general_information",
            "url_tail": "general-information",
            "workbook_number": None,
        }
    ),
    "tribal_data_consent": SectionBabelFish(
        **{
            "all_caps": "TRIBAL_DATA_CONSENT",
            "camel_case": "TribalDataConsent",
            "friendly": "Tribal Data Sharing Consent",
            "friendly_title": "Tribal Data Sharing Consent form",
            "reverse_url": None,
            "snake_case": "tribal_data_consent",
            "url_tail": None,
            "workbook_number": None,
        }
    ),
}


def find_section_by_name(name):
    """
    Find the answers, first trying snake_case and then all the other versions.
    """
    if name in section_names:
        return section_names[name]

    for guide in section_names.values():
        if name in guide:
            return guide

    return None
