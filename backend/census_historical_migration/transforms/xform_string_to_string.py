def string_to_string(value):
    """
    Converts a string to a trimmed string. Returns an empty string if the input
    is None."""
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value).__name__}")
    trimmed_value = value.strip()

    return trimmed_value
