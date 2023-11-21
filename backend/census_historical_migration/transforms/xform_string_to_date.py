from datetime import datetime


def string_to_date(value):
    """Converts a string to a date."""
    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value).__name__}")

    value = value.strip()

    # Check if the string can be converted to a date
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"Cannot convert string to date: '{value}'")
