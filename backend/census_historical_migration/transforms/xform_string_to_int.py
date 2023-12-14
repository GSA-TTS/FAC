def string_to_int(value):
    """Converts a string to an integer."""

    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value).__name__}")
    value = value.strip()
    # Check if the string can be converted to an integer
    try:
        return int(value)
    except ValueError:
        raise ValueError(f"Cannot convert string to integer: '{value}'")
