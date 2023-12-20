from ..exception_utils import DataMigrationValueError


def string_to_string(value):
    """
    Converts a string to a trimmed string. Returns an empty string if the input
    is None."""
    if value is None:
        return ""
    elif not isinstance(value, str):
        raise DataMigrationValueError(
            f"Expected string, got {type(value).__name__}",
            "invalid_str_type",
        )

    return value.strip()
