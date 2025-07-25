import os
import json
import logging

from jsonschema import Draft7Validator, FormatChecker, validate
from jsonschema.exceptions import ValidationError as JSONSchemaValidationError

from django.core.exceptions import ValidationError

from django.utils.translation import gettext_lazy as _
from django.conf import settings
import requests
from openpyxl import load_workbook
from pypdf import PdfReader

from audit.intakelib import (
    additional_ueis_named_ranges,
    additional_eins_named_ranges,
    corrective_action_plan_named_ranges,
    federal_awards_named_ranges,
    audit_findings_text_named_ranges,
    audit_findings_named_ranges,
    secondary_auditors_named_ranges,
    notes_to_sefa_named_ranges,
)
from audit.fixtures.excel import (
    ADDITIONAL_UEIS_TEMPLATE_DEFINITION,
    ADDITIONAL_EINS_TEMPLATE_DEFINITION,
    CORRECTIVE_ACTION_TEMPLATE_DEFINITION,
    FEDERAL_AWARDS_TEMPLATE_DEFINITION,
    FINDINGS_TEXT_TEMPLATE_DEFINITION,
    FINDINGS_UNIFORM_TEMPLATE_DEFINITION,
    SECONDARY_AUDITORS_TEMPLATE_DEFINITION,
    NOTES_TO_SEFA_TEMPLATE_DEFINITION,
)
from support.decorators import newrelic_timing_metric


logger = logging.getLogger(__name__)


MAX_EXCEL_FILE_SIZE_MB = 25
MAX_SINGLE_AUDIT_REPORT_FILE_SIZE_MB = 30

ALLOWED_EXCEL_FILE_EXTENSIONS = [".xlsx"]
ALLOWED_SINGLE_AUDIT_REPORT_EXTENSIONS = [".pdf"]

ALLOWED_EXCEL_CONTENT_TYPES = [
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
]
ALLOWED_SINGLE_AUDIT_REPORT_CONTENT_TYPES = [
    "application/pdf",
]

# https://github.com/ajilaag/clamav-rest#status-codes
AV_SCAN_CODES = {
    "CLEAN": [200],
    "INFECTED": [406],
    "ERROR": [400, 412, 500, 501],
}

XLSX_TEMPLATE_DEFINITION_DIR = settings.XLSX_TEMPLATE_JSON_DIR

ErrorDetails = list[tuple[str, str, str, str]]


def validate_uei(value):
    """Validates the UEI using the UEI Spec"""
    validate_uei_length(value)
    validate_uei_alphanumeric(value)
    validate_uei_valid_chars(value)
    validate_uei_leading_char(value)
    validate_uei_nine_digit_sequences(value)
    return value


def validate_uei_length(value):
    if not len(value) == 12:
        raise ValidationError(_("The UEI should be 12 characters long"))
    return value


def validate_uei_alphanumeric(value):
    """The UEI should be alphanumeric"""
    if not value.isalnum():
        raise ValidationError(
            _("The UEI should be alphanumeric"),
        )
    return value


def validate_uei_valid_chars(value):
    """The letters “O” and “I” are not used to avoid confusion with zero and one."""
    if "O" in value.upper() or "I" in value.upper():
        raise ValidationError(
            _(
                "The letters “O” and “I” are not used to avoid confusion with zero and one."
            ),
        )
    return value


def validate_uei_leading_char(value):
    """The first character is not zero to avoid cutting off digits that can occur during data imports,
    for example, when importing data into spreadsheet programs."""
    if value.startswith("0"):
        raise ValidationError(
            _(
                "The first character is not zero to avoid cutting off digits that can occur during data imports."
            ),
        )
    return value


def validate_uei_nine_digit_sequences(value):
    """Nine-digit sequences are not used in the identifier to avoid collision with the nine-digit
    DUNS Number or Taxpayer Identification Number (TIN)."""
    count = 0
    for ch in value:
        if ch.isnumeric():
            count += 1
        else:
            count = 0

        if count >= 9:
            raise ValidationError(
                _(
                    "Nine-digit sequences are not used in the identifier to avoid collision with the nine-digit DUNS Number or Taxpayer Identification Number (TIN)."
                ),
            )
    return value


def validate_findings_uniform_guidance_json(value):
    """
    Apply JSON Schema for findings uniform guidance and report errors.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "FederalAwardsAuditFindings.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(value))
    if len(errors) > 0:
        raise ValidationError(message=_findings_uniform_guidance_json_error(errors))


def validate_additional_ueis_json(value):
    """
    Apply JSON Schema for additional UEIs and report errors.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "AdditionalUEIs.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(value))
    if len(errors) > 0:
        raise ValidationError(message=_additional_ueis_json_error(errors))


def validate_additional_eins_json(value):
    """
    Apply JSON Schema for additional EINs and report errors.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "AdditionalEINs.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(value))
    if len(errors) > 0:
        raise ValidationError(message=_additional_eins_json_error(errors))


def validate_notes_to_sefa_json(value):
    """
    Apply JSON Schema for notes to SEFA and report errors.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "NotesToSefa.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(value))
    if len(errors) > 0:
        raise ValidationError(message=_notes_to_sefa_json_error(errors))


def validate_findings_text_json(value):
    """
    Apply JSON Schema for findings text and report errors.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "AuditFindingsText.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(value))
    if len(errors) > 0:
        raise ValidationError(message=_findings_text_json_error(errors))


def validate_corrective_action_plan_json(value):
    """
    Apply JSON Schema for corrective action plan and report errors.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "CorrectiveActionPlan.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(value))
    if len(errors) > 0:
        raise ValidationError(message=_corrective_action_json_error(errors))


def validate_federal_award_json(value):
    """
    Apply JSON Schema for federal awards and report errors.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "FederalAwards.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(value))
    if len(errors) > 0:
        raise ValidationError(message=_federal_awards_json_error(errors))


def validate_general_information_schema(general_information):
    """
    Apply JSON Schema for general information and report errors.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "GeneralInformationRequired.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft7Validator(schema, format_checker=FormatChecker())
    try:
        for key, val in general_information.items():
            if key in schema["properties"] and val not in [None, "", [], {}]:
                field_schema = {
                    "type": "object",
                    "properties": {key: schema["properties"][key]},
                }
                validator.validate({key: val}, field_schema)
    except JSONSchemaValidationError as err:
        logger.error(
            f"ValidationError in General Information: Invalid value: {val} for key: {key}"
        )
        raise ValidationError(
            _(err.message),
        ) from err
    return general_information


def validate_use_of_gsa_migration_keyword(general_information, is_data_migration):
    """Check if GSA_MIGRATION keyword is used and is allowed to be used in general information"""

    if not is_data_migration and settings.GSA_MIGRATION in [
        general_information.get("auditee_email", ""),
        general_information.get("auditor_email", ""),
        general_information.get("auditee_uei", ""),
        general_information.get("ein", ""),
        general_information.get("auditor_ein", ""),
        general_information.get("auditee_zip", ""),
        general_information.get("auditor_zip", ""),
    ]:
        raise ValidationError(
            _(f"{settings.GSA_MIGRATION} not permitted outside of migrations"),
        )

    return general_information


def validate_use_of_gsa_migration_keyword_in_audit_info(
    audit_information, is_data_migration
):
    """Check if GSA_MIGRATION keyword is used and is allowed to be used in audit information"""

    if not is_data_migration and settings.GSA_MIGRATION in [
        audit_information.get("is_sp_framework_required", ""),
        audit_information.get("is_low_risk_auditee", ""),
        audit_information.get("is_going_concern_included", ""),
        audit_information.get("is_internal_control_deficiency_disclosed", ""),
        audit_information.get("is_internal_control_material_weakness_disclosed", ""),
        audit_information.get("is_material_noncompliance_disclosed", ""),
        audit_information.get("is_aicpa_audit_guide_included", ""),
        ",".join(audit_information.get("agencies", [])),
        ",".join(audit_information.get("gaap_results", [])),
    ]:
        raise ValidationError(
            _(f"{settings.GSA_MIGRATION} not permitted outside of migrations"),
        )

    return audit_information


def validate_general_information_schema_rules(general_information):
    """Check general information schema rules"""

    # Check for invalid 'audit_period_other_months' usage
    if general_information.get("audit_period_covered") in [
        "annual",
        "biennial",
    ] and general_information.get("audit_period_other_months"):
        if general_information.get("audit_period_other_months"):
            raise ValidationError(
                _(
                    "Invalid Audit Period - 'Audit period months' should not be set for 'annual' or 'biennial' Audit periods"
                )
            )
    # Ensure 'audit_period_other_months' is provided for 'other' audit period
    elif general_information.get(
        "audit_period_covered"
    ) == "other" and not general_information.get("audit_period_other_months"):
        raise ValidationError(
            _(
                "Invalid Audit Period - 'Audit period months' must be set for 'other' Audit period"
            ),
        )

    # Validate USA auditor information
    if general_information.get("auditor_country") == "USA" and (
        not general_information.get("auditor_zip")
        or not general_information.get("auditor_state")
        or not general_information.get("auditor_address_line_1")
        or not general_information.get("auditor_city")
    ):
        raise ValidationError(_("Missing Auditor Street or City or State or Zip Code"))

    # Validate non-USA auditor state or zip code should not be provided
    elif general_information.get("auditor_country") != "USA" and (
        general_information.get("auditor_zip")
        or general_information.get("auditor_state")
        or general_information.get("auditor_city")
        or general_information.get("auditor_address_line_1")
    ):
        raise ValidationError(
            _(
                "Invalid Auditor Street or City or State or Zip Code for non-USA countries"
            )
        )
    # Validate non-USA auditor address is provided
    elif general_information.get("auditor_country") != "USA" and not (
        general_information.get("auditor_international_address")
    ):
        raise ValidationError(_("Missing Auditor International Address"))

    return general_information


def validate_general_information_json(value, is_data_migration=True):
    """
    Apply JSON Schema and Python checks to a general information record.

    Keyword arguments:
    is_data_migration -- True if ignoring GSA_MIGRATION emails. (default True)
    """
    validate_use_of_gsa_migration_keyword(value, is_data_migration)
    validate_general_information_schema(value)

    return value


def validate_general_information_complete_json(value, is_data_migration=True):
    """
    Apply JSON Schema and Python checks to a general information record.
    Performs additional checks to enforce completeness.

    Keyword arguments:
    is_data_migration -- True if ignoring GSA_MIGRATION emails. (default True)
    """
    validate_use_of_gsa_migration_keyword(value, is_data_migration)
    validate_general_information_schema(value)
    validate_general_information_schema_rules(value)

    return value


def validate_audit_information_json(value, is_data_migration=True):
    """
    Apply JSON Schema and Python checks to audit information record.

    Keyword arguments:
    is_data_migration -- True if ignoring GSA_MIGRATION emails. (default True)
    """

    validate_use_of_gsa_migration_keyword_in_audit_info(value, is_data_migration)
    validate_audit_information_schema(value)
    return value


def validate_audit_information_schema(value):
    """
    Apply JSON Schema for audit information and report errors.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "AuditInformation.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    try:
        validate(value, schema, format_checker=FormatChecker())
    except JSONSchemaValidationError as err:
        raise ValidationError(
            _(err.message),
        ) from err
    return value


def validate_secondary_auditors_json(value):
    """
    Apply JSON Schema for secondary auditors and report errors.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "SecondaryAuditors.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(value))
    if len(errors) > 0:
        raise ValidationError(message=_secondary_auditors_json_error(errors))


def validate_auditor_certification_json(value):
    """
    Apply JSON Schema for auditor certification and report errors.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "AuditorCertification.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    try:
        validate(value, schema, format_checker=FormatChecker())
    except JSONSchemaValidationError as err:
        raise ValidationError(
            _(err.message),
        ) from err
    return value


def validate_auditee_certification_json(value):
    """
    Apply JSON Schema for auditee certification and report errors.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "AuditeeCertification.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    try:
        validate(value, schema, format_checker=FormatChecker())
    except JSONSchemaValidationError as err:
        raise ValidationError(
            _(err.message),
        ) from err
    return value


def validate_tribal_data_consent_json(value):
    """
    Apply JSON Schema for tribal data consent and report errors.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "TribalAccess.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    try:
        validate(value, schema, format_checker=FormatChecker())
    except JSONSchemaValidationError as err:
        raise ValidationError(
            _(err.message),
        ) from err
    return value


def validate_file_extension(file, allowed_extensions):
    """
    User-provided filenames must be have an allowed extension
    """
    _, extension = os.path.splitext(file.name)

    logger.info(f"Uploaded file {file.name} extension: {extension}")

    if not extension.lower() in allowed_extensions:
        raise ValidationError(
            f"Invalid extension - allowed extensions are {', '.join(allowed_extensions)}"
        )

    return extension


def validate_file_content_type(file, allowed_content_types):
    """
    Files must have an allowed content (MIME) type
    """
    logger.info(f"Uploaded file {file.name} content-type: {file.file.content_type}")

    if file.file.content_type not in allowed_content_types:
        raise ValidationError(
            f"Invalid content type - allowed types are {', '.join(allowed_content_types)}"
        )

    return file.file.content_type


def validate_file_size(file, max_file_size_mb):
    """Files must be under the maximum allowed file size"""
    max_file_size = max_file_size_mb * 1024 * 1024

    logger.info(
        f"Uploaded file {file.name} size: {file.size} (max allowed: {max_file_size})"
    )

    if file.size > max_file_size:
        file_size_mb = round(file.size / 1024 / 1024, 2)
        raise ValidationError(
            f"This file size is: {file_size_mb} MB this cannot be uploaded, maximum allowed: {max_file_size_mb} MB"
        )

    return file.size


def _scan_file(file):
    error_message = "We were unable to complete a security inspection of the file, please try again or contact support for assistance."

    try:
        return requests.post(
            settings.AV_SCAN_URL,
            files={"file": file},
            data={"name": file.name},
            timeout=45,
        )
    # Common upload issues get their own messages. These messages display as form errors.
    # Allow other errors to be raised and either caught elsewhere or passed to a 400 page.
    except requests.exceptions.ConnectionError:
        raise ValidationError(f"Connection error. {error_message}")
    except requests.exceptions.ReadTimeout:
        raise ValidationError(f"Read timed out. {error_message}")


@newrelic_timing_metric("validate_file_infection")
def validate_file_infection(file):
    """Files must pass an AV scan"""
    logger.info(f"Attempting to scan file: {file}.")

    attempt = 1

    # on large(ish) files (>10mb), the clamav-rest API sometimes times out
    # on the first couple of attempts. We retry the scan up to our maximum
    # in these cases
    while (res := _scan_file(file)).status_code in AV_SCAN_CODES["ERROR"]:
        if (attempt := attempt + 1) > settings.AV_SCAN_MAX_ATTEMPTS:
            break

        logger.info(f"Scan attempt {attempt} failed, trying again...")
        file.seek(0)

    if res.status_code not in AV_SCAN_CODES["CLEAN"]:
        logger.info(f"Scan of {file} revealed potential infection - rejecting!")
        raise ValidationError(
            "The file you uploaded did not pass our security inspection, upload failed!"
        )

    logger.info(f"Scanning of file {file} complete.")


def validate_excel_file_integrity(file):
    """Files must be readable by openpyxl"""
    try:
        logger.info(f"Attempting to load workbook from {file.name}")
        load_workbook(filename=file)
        logger.info(f"Successfully loaded workbook from {file.name}")
    except Exception:
        raise ValidationError("We were unable to process the file you uploaded.")


def validate_excel_file(file):
    validate_file_extension(file, ALLOWED_EXCEL_FILE_EXTENSIONS)
    validate_file_content_type(file, ALLOWED_EXCEL_CONTENT_TYPES)
    validate_file_size(file, MAX_EXCEL_FILE_SIZE_MB)
    validate_file_infection(file)
    validate_excel_file_integrity(file)


def _get_error_details(xlsx_definition_template, named_ranges_row_indices):
    """Retrieve error details given an XLSX template definition and a list of JSONSchemaValidationError"""
    error_details: ErrorDetails = []
    for named_range, row_index in named_ranges_row_indices:
        # Loop over all sheets instead of accessing them directly
        for sheet in xlsx_definition_template["sheets"]:
            # Check if "open_ranges" key is present in the sheet
            if "open_ranges" in sheet:
                for open_range in sheet["open_ranges"]:
                    if open_range["range_name"] == named_range:
                        error_details.append(
                            (
                                open_range["title_cell"][0],
                                xlsx_definition_template["title_row"] + row_index + 1,
                                open_range["title"],
                                open_range["help"],
                            )
                        )
                        break  # Break the loop once the named_range is found
            # Check if "single_cells" key is present in the sheet
            if "single_cells" in sheet:
                for single_cell in sheet["single_cells"]:
                    if single_cell["range_name"] == named_range:
                        error_details.append(
                            (
                                single_cell["range_cell"][0],
                                single_cell["range_cell"][1],
                                single_cell["title"],
                                single_cell["help"],
                            )
                        )
                        break  # Break the loop once the named_range is found
    return error_details


def _corrective_action_json_error(errors):
    """Process JSON Schema errors for corrective actions"""
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / CORRECTIVE_ACTION_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    return _get_error_details(template, corrective_action_plan_named_ranges(errors))


def _federal_awards_json_error(errors):
    """Process JSON Schema errors for federal actions"""
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / FEDERAL_AWARDS_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    return _get_error_details(template, federal_awards_named_ranges(errors))


def _findings_text_json_error(errors):
    """Process JSON Schema errors for findings text"""
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / FINDINGS_TEXT_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    return _get_error_details(template, audit_findings_text_named_ranges(errors))


def _findings_uniform_guidance_json_error(errors):
    """Process JSON Schema errors for findings uniform guidance"""
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / FINDINGS_UNIFORM_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    return _get_error_details(template, audit_findings_named_ranges(errors))


def _secondary_auditors_json_error(errors):
    """Process JSON Schema errors for secondary auditors"""
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / SECONDARY_AUDITORS_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    return _get_error_details(template, secondary_auditors_named_ranges(errors))


def validate_single_audit_report_file_extension(file):
    """
    User-provided filenames must be have an allowed extension
    """
    _, extension = os.path.splitext(file.name)

    logger.info(f"Uploaded file {file.name} extension: {extension}")

    if not extension.lower() in ALLOWED_EXCEL_FILE_EXTENSIONS:
        raise ValidationError(
            f"Invalid extension - allowed extensions are {', '.join(ALLOWED_EXCEL_FILE_EXTENSIONS)}"
        )

    return extension


def validate_pdf_file_integrity(file):
    """Files must be readable PDFs"""
    MIN_CHARARACTERS_IN_PDF = 6000
    MIN_PERCENT_READABLE_PAGES = 0.50

    try:
        reader = PdfReader(file)

        if reader.is_encrypted:
            raise ValidationError(
                "We were unable to process the file you uploaded because it is encrypted."
            )

        total_chars = 0
        num_pages_with_text = 0

        for page in reader.pages:
            page_text = page.extract_text()
            total_chars += len(page_text)
            num_pages_with_text += 1 if len(page_text) else 0

        percent_readable_pages = num_pages_with_text / len(reader.pages)

        if total_chars == 0:
            raise ValidationError(
                "We were unable to process the file you uploaded because it contains no readable text."
            )
        elif total_chars < MIN_CHARARACTERS_IN_PDF:
            raise ValidationError(
                "We were unable to process the file you uploaded because it contains too little readable text."
            )
        elif percent_readable_pages < MIN_PERCENT_READABLE_PAGES:
            raise ValidationError(
                f"We were unable to process the file you uploaded because only {percent_readable_pages:.0%} of the pages contain readable text (minimum {MIN_PERCENT_READABLE_PAGES:.0%} required.)"
            )

    except ValidationError:
        raise
    except Exception:
        raise ValidationError("We were unable to process the file you uploaded.")


def validate_single_audit_report_file(file):
    validate_file_extension(file, ALLOWED_SINGLE_AUDIT_REPORT_EXTENSIONS)
    validate_file_content_type(file, ALLOWED_SINGLE_AUDIT_REPORT_CONTENT_TYPES)
    validate_file_size(file, MAX_SINGLE_AUDIT_REPORT_FILE_SIZE_MB)
    validate_file_infection(file)
    validate_pdf_file_integrity(file)


def _additional_ueis_json_error(errors):
    """Process JSON Schema errors for additional UEIs"""
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / ADDITIONAL_UEIS_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    return _get_error_details(template, additional_ueis_named_ranges(errors))


def _additional_eins_json_error(errors):
    """Process JSON Schema errors for additional EINs"""
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / ADDITIONAL_EINS_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    return _get_error_details(template, additional_eins_named_ranges(errors))


def _notes_to_sefa_json_error(errors):
    """Process JSON Schema errors for notes to sefa"""
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / NOTES_TO_SEFA_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    return _get_error_details(template, notes_to_sefa_named_ranges(errors))


def validate_component_page_numbers(obj):
    required_keys = [
        "financial_statements",
        "financial_statements_opinion",
        "schedule_expenditures",
        "schedule_expenditures_opinion",
        "uniform_guidance_control",
        "uniform_guidance_compliance",
        "GAS_control",
        "GAS_compliance",
        "schedule_findings",
    ]
    optional_keys = ["schedule_prior_findings", "CAP_page"]

    required_keys_are_good = all(
        [((key in obj) and isinstance(obj[key], int)) for key in required_keys]
    )
    optional_keys_are_good = all(
        [
            ((key not in obj) or ((key in obj) and isinstance(obj[key], int)))
            for key in optional_keys
        ]
    )
    return required_keys_are_good and optional_keys_are_good
