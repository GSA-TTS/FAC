def string_to_bool(value):
    """Converts a string to a boolean."""

    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value).__name__}")

    new_value = value.strip().upper()
    if new_value not in ["Y", "N"]:
        raise ValueError(f"Expected 'Y' or 'N', got '{value}'")

    return new_value == "Y"
