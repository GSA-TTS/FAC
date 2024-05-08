from ..exception_utils import DataMigrationValueError

from django.conf import settings


def uppercase_y_or_n(value):
    """Converts 'y' to 'Y' and 'n' to 'N', and allows GSA_MIGRATION"""

    if not isinstance(value, str):
        raise DataMigrationValueError(
            f"Expected string, got {type(value).__name__}",
            "uppercase_y_or_n",
        )

    if value == settings.GSA_MIGRATION:
        return value

    new_value = value.strip().upper()
    if new_value not in ["Y", "N"]:
        raise DataMigrationValueError(
            f"Expected 'Y', 'y', 'N', 'n', or ${settings.GSA_MIGRATION}, got '{value}'",
            "uppercase_y_or_n",
        )

    return new_value
