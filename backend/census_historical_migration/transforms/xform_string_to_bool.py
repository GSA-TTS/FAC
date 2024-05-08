from ..exception_utils import DataMigrationValueError
from django.conf import settings


def string_to_bool(value):
    """Converts a string to a boolean."""

    if not isinstance(value, str):
        raise DataMigrationValueError(
            f"Expected string, got {type(value).__name__}",
            "invalid_str_type",
        )

    new_value = value.strip().upper()

    if new_value == settings.GSA_MIGRATION:
        return new_value

    if new_value not in ["Y", "N"]:
        raise DataMigrationValueError(
            f"Expected 'Y' or 'N', got '{value}'",
            "invalid_y_or_n",
        )

    return new_value == "Y"
