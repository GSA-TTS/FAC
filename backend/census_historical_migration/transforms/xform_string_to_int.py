from ..exception_utils import DataMigrationValueError


def string_to_int(value):
    """Converts a string to an integer."""

    if not isinstance(value, str):
        raise DataMigrationValueError(
            f"Expected string, got {type(value).__name__}",
            "invalid_str_type",
        )
    value = value.strip()
    # Check if the string can be converted to an integer
    try:
        return int(value)
    except ValueError:
        raise DataMigrationValueError(
            f"Cannot convert string to integer: '{value}'",
            "str_to_int_conversion",
        )
