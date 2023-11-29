def string_to_string(value):
    """
    Converts a string to a trimmed string. Returns an empty string if the input
    is empty or 'nan'."""
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError(f"Expected string, got {type(value).__name__}")
    trimmed_value = value.strip()
    # FIXME-MSHD: When some CSV files are loaded
    # to Postgres DB, empty string are being converted into 'nan'
    # This is a temporary fix to handle the issue, we need to investigate this further.
    return "" if trimmed_value in ["nan"] else trimmed_value
