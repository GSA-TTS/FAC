from pathlib import Path
import json
import jsonschema
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings


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


def validate_federal_award_json(value):
    """
    Apply JSON Schema for federal awards and report errors.
    """
    root = Path(settings.SECTION_SCHEMA_DIR)
    schema_path = root / "FederalAwards.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    try:
        jsonschema.validate(value, schema)
    except jsonschema.exceptions.ValidationError as err:
        raise ValidationError(
            _(err.message),
        ) from err
    return value


def validate_general_information_json(value):
    """
    Apply JSON Schema for general information and report errors.
    """
    root = Path(settings.SECTION_SCHEMA_DIR)
    schema_path = root / "GeneralInformation.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    try:
        jsonschema.validate(value, schema, format_checker=jsonschema.FormatChecker())
    except jsonschema.exceptions.ValidationError as err:
        raise ValidationError(
            _(err.message),
        ) from err
    return value
