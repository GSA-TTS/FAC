class Util:
    @staticmethod
    def bool_to_yes_no(condition):
        """Convert a boolean value to 'Yes' or 'No'."""
        return "Yes" if condition else "No"

    @staticmethod
    def optional_bool(condition):
        """Convert a boolean value or None to a string representation."""
        if condition is None:
            return ""
        else:
            return "Yes" if condition else "No"

    @staticmethod
    def json_array_to_str(json_array):
        """Convert a JSON array to a string representation."""
        if json_array is None:
            return ""
        elif isinstance(json_array, list):
            return ", ".join(map(str, json_array))
        else:
            # FIXME This should raise an error
            return f"NOT AN ARRAY: {json_array}"


class ExcelExtractionError(Exception):
    def __init__(
        self,
        message="An error occurred during data extraction from this workbook",
        error_key=None,
    ):
        self.message = message
        self.error_key = error_key
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} (Error Key: {self.error_key})"


def match_first_get_second(tuples, pattern, default=None):
    """
    Given a set of tuples, return the second value in the first tuple where the
    first value matches the pattern.
    """
    return next((s[1] for s in tuples if s[0] == pattern), default)
