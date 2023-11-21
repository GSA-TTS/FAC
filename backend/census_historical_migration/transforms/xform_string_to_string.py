def string_to_string(value):
    """Converts a string to a string."""
    if isinstance(value, str):
        return value.strip()
    else:
        raise ValueError(f"Expected string, got {type(value).__name__}")
