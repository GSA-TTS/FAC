def string_to_bool(value):
    """Converts a string to a boolean."""

    if isinstance(value, bool):
        return value

    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value).__name__}")

    value = value.strip()
    if len(value) > 1:
        raise ValueError(f"Expected string of length 1, got {len(value)}")

    return value.upper() == "Y"
