import os
import json
from jsonschema import Draft7Validator, FormatChecker, validate
from jsonschema.exceptions import ValidationError as JSONSchemaValidationError
import logging
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import requests
from slugify import slugify
from openpyxl import load_workbook

from audit.excel import (
    corrective_action_plan_named_ranges,
    federal_awards_named_ranges,
    findings_text_named_ranges,
    findings_uniform_guidance_named_ranges,
)
from audit.fixtures.excel import (
    CORRECTIVE_ACTION_TEMPLATE_DEFINITION,
    FEDERAL_AWARDS_TEMPLATE_DEFINITION,
    FINDINGS_TEXT_TEMPLATE_DEFINITION,
    FINDINGS_UNIFORM_TEMPLATE_DEFINITION,
)


logger = logging.getLogger(__name__)


MAX_EXCEL_FILE_SIZE_MB = 25

ERROR_MESSAGE = "No input found or invalid input provided."

ALLOWED_EXCEL_FILE_EXTENSIONS = [".xls", ".xlsx"]

ALLOWED_EXCEL_CONTENT_TYPES = [
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
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
    validate_uei_alphanumeric(value)
    validate_uei_valid_chars(value)
    validate_uei_leading_char(value)
    validate_uei_nine_digit_sequences(value)
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
    schema_path = settings.SECTION_SCHEMA_DIR / "FindingsUniformGuidance.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    validator = Draft7Validator(schema)
    errors = list(validator.iter_errors(value))
    if len(errors) > 0:
        raise ValidationError(message=_findings_uniform_guidance_json_error(errors))


def validate_findings_text_json(value):
    """
    Apply JSON Schema for findings text and report errors.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "FindingsText.schema.json"
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


def validate_general_information_json(value):
    """
    Apply JSON Schema for general information and report errors.
    """
    schema_path = settings.SECTION_SCHEMA_DIR / "GeneralInformation.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    try:
        validate(value, schema, format_checker=FormatChecker())
    except JSONSchemaValidationError as err:
        raise ValidationError(
            _(err.message),
        ) from err
    return value


def validate_excel_filename(file):
    """
    User-provided filenames are slugified during validation
    """
    filename, extension = os.path.splitext(file.name)

    if len(filename) == 0:
        raise ValidationError("Invalid filename")

    if len(extension) == 0:
        raise ValidationError("Invalid filename")

    slugified = slugify(filename)

    logger.info(f"Uploaded file {file.name} slugified filename: {slugified}")

    if len(slugified) == 0:
        raise ValidationError("Invalid filename")

    return f"{slugified}{extension}"


def validate_excel_file_extension(file):
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


def validate_excel_file_content_type(file):
    """
    Files must have an allowed content (MIME) type
    """
    logger.info(f"Uploaded file {file.name} content-type: {file.file.content_type}")

    if file.file.content_type not in ALLOWED_EXCEL_CONTENT_TYPES:
        raise ValidationError(
            f"Invalid content type - allowed types are {', '.join(ALLOWED_EXCEL_CONTENT_TYPES)}"
        )

    return file.file.content_type


def validate_excel_file_size(file):
    """Files must be under the maximum allowed file size"""
    max_file_size = MAX_EXCEL_FILE_SIZE_MB * 1024 * 1024

    logger.info(
        f"Uploaded file {file.name} size: {file.size} (max allowed: {max_file_size})"
    )

    if file.size > max_file_size:
        file_size_mb = round(file.size / 1024 / 1024, 2)
        raise ValidationError(
            f"This file size is: {file_size_mb} MB this cannot be uploaded, maximum allowed: {MAX_EXCEL_FILE_SIZE_MB} MB"
        )

    return file.size


def _scan_file(file):
    try:
        return requests.post(
            settings.AV_SCAN_URL,
            files={"file": file},
            data={"name": file.name},
            timeout=15,
        )
    except requests.exceptions.ConnectionError:
        raise ValidationError(
            "We were unable to complete a security inspection of the file, please try again or contact support for assistance."
        )


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
    validate_excel_filename(file)
    validate_excel_file_extension(file)
    validate_excel_file_content_type(file)
    validate_excel_file_size(file)
    validate_file_infection(file)
    validate_excel_file_integrity(file)


def _get_error_details(xlsx_definition_template, named_ranges_row_indices):
    """Retrieve error details givenn an XLSX template definition and a list of JSONSchemaValidationError"""
    error_details: ErrorDetails = []
    for named_range, row_index in named_ranges_row_indices:
        for open_range in xlsx_definition_template["sheets"][0]["open_ranges"]:
            if open_range["range_name"] == named_range:
                error_details.append(
                    (
                        open_range["title_cell"][0],
                        xlsx_definition_template["title_row"] + row_index + 1,
                        open_range["title"],
                        ERROR_MESSAGE,
                    )
                )
                break
        for single_cell in xlsx_definition_template["sheets"][0]["single_cells"]:
            if single_cell["range_name"] == named_range:
                error_details.append(
                    (
                        single_cell["range_cell"][0],
                        single_cell["range_cell"][1],
                        single_cell["title"],
                        ERROR_MESSAGE,
                    )
                )
                break
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
    return _get_error_details(template, findings_text_named_ranges(errors))


def _findings_uniform_guidance_json_error(errors):
    """Process JSON Schema errors for findings uniform guidance"""
    template_definition_path = (
        XLSX_TEMPLATE_DEFINITION_DIR / FINDINGS_UNIFORM_TEMPLATE_DEFINITION
    )
    template = json.loads(template_definition_path.read_text(encoding="utf-8"))
    return _get_error_details(template, findings_uniform_guidance_named_ranges(errors))
