from django.conf import settings
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme

from audit.fixtures.excel import FORM_SECTIONS
from audit.intakelib import (
    extract_additional_ueis,
    extract_additional_eins,
    extract_federal_awards,
    extract_corrective_action_plan,
    extract_audit_findings_text,
    extract_audit_findings,
    extract_secondary_auditors,
    extract_notes_to_sefa,
)
from audit.intakelib.mapping_additional_eins import additional_eins_audit_view
from audit.intakelib.mapping_additional_ueis import additional_ueis_audit_view
from audit.intakelib.mapping_audit_findings import findings_audit_view
from audit.intakelib.mapping_audit_findings_text import audit_findings_text_audit_view
from audit.intakelib.mapping_corrective_action_plan import (
    corrective_action_plan_audit_view,
)
from audit.intakelib.mapping_federal_awards import federal_awards_audit_view
from audit.intakelib.mapping_notes_to_sefa import notes_to_sefa_audit_view
from audit.intakelib.mapping_secondary_auditors import secondary_auditors_audit_view
from audit.validators import (
    validate_additional_ueis_json,
    validate_additional_eins_json,
    validate_corrective_action_plan_json,
    validate_federal_award_json,
    validate_findings_text_json,
    validate_findings_uniform_guidance_json,
    validate_notes_to_sefa_json,
    validate_secondary_auditors_json,
)


class Util:
    @staticmethod
    def bool_to_yes_no(condition):
        """Convert a boolean value to 'Yes' or 'No'."""
        if condition == settings.GSA_MIGRATION:
            return condition
        else:
            return "Yes" if condition else "No"

    @staticmethod
    def optional_bool(condition):
        """Convert a boolean value or None to a string representation."""
        if condition is None:
            return ""
        elif condition == settings.GSA_MIGRATION:
            return condition
        else:
            return "Yes" if condition else "No"

    @staticmethod
    def json_array_to_str(json_array):
        """Convert a JSON array to a string representation."""
        if json_array is None:
            return ""
        elif isinstance(json_array, list):
            return ",".join(map(str, json_array))
        else:
            # FIXME This should raise an error
            return f"NOT AN ARRAY: {json_array}"

    @staticmethod
    def remove_extra_fields(general_information_data):
        """Remove unnecessary fields from general information data."""
        # Remove unnecessary fields based on auditor_country and auditor_international_address
        # If auditor country is USA, remove the international address field
        if general_information_data.get("auditor_country") == "USA":
            general_information_data.pop("auditor_international_address", None)
        # If auditor country is not USA, remove the USA address fields
        elif general_information_data.get("auditor_country") != "USA":
            general_information_data.pop("auditor_address_line_1", None)
            general_information_data.pop("auditor_city", None)
            general_information_data.pop("auditor_state", None)
            general_information_data.pop("auditor_zip", None)
        # Remove unnecessary fields based on audit_period_covered
        # If audit_period_covered is not "other", remove the audit_period_other_months field
        if general_information_data.get("audit_period_covered") != "other":
            general_information_data.pop("audit_period_other_months", None)
        return general_information_data

    @staticmethod
    def validate_redirect_url(url):
        """Ensure that the url received is safe to redirect to."""
        if url_has_allowed_host_and_scheme(url, allowed_hosts=None):
            return redirect(url)
        else:
            return redirect("/")


class ExcelExtractionError(Exception):
    def __init__(
        self,
        message="An error occurred during data extraction from this workbook",
        error_key=None,
    ):
        self.message = message
        self.error_key = error_key
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (Error Key: {self.error_key})"


FORM_SECTION_HANDLERS = {
    FORM_SECTIONS.FEDERAL_AWARDS: {
        "extractor": extract_federal_awards,
        "field_name": "federal_awards",
        "validator": validate_federal_award_json,
        "audit_object": federal_awards_audit_view,
    },
    FORM_SECTIONS.CORRECTIVE_ACTION_PLAN: {
        "extractor": extract_corrective_action_plan,
        "field_name": "corrective_action_plan",
        "validator": validate_corrective_action_plan_json,
        "audit_object": corrective_action_plan_audit_view,
    },
    FORM_SECTIONS.FINDINGS_UNIFORM_GUIDANCE: {
        "extractor": extract_audit_findings,
        "field_name": "findings_uniform_guidance",
        "validator": validate_findings_uniform_guidance_json,
        "audit_object": findings_audit_view,
    },
    FORM_SECTIONS.FINDINGS_TEXT: {
        "extractor": extract_audit_findings_text,
        "field_name": "findings_text",
        "validator": validate_findings_text_json,
        "audit_object": audit_findings_text_audit_view,
    },
    FORM_SECTIONS.ADDITIONAL_UEIS: {
        "extractor": extract_additional_ueis,
        "field_name": "additional_ueis",
        "validator": validate_additional_ueis_json,
        "audit_object": additional_ueis_audit_view,
    },
    FORM_SECTIONS.ADDITIONAL_EINS: {
        "extractor": extract_additional_eins,
        "field_name": "additional_eins",
        "validator": validate_additional_eins_json,
        "audit_object": additional_eins_audit_view,
    },
    FORM_SECTIONS.SECONDARY_AUDITORS: {
        "extractor": extract_secondary_auditors,
        "field_name": "secondary_auditors",
        "validator": validate_secondary_auditors_json,
        "audit_object": secondary_auditors_audit_view,
    },
    FORM_SECTIONS.NOTES_TO_SEFA: {
        "extractor": extract_notes_to_sefa,
        "field_name": "notes_to_sefa",
        "validator": validate_notes_to_sefa_json,
        "audit_object": notes_to_sefa_audit_view,
    },
}
