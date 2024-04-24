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
            return ",".join(map(str, json_array))
        else:
            # FIXME This should raise an error
            return f"NOT AN ARRAY: {json_array}"

    @staticmethod
    def remove_extra_fields(general_information_data):
        """Remove unnecessary fields from general information data."""
        # Remove unnecessary fields based on auditor_country and auditor_international_address
        # If auditor country is USA, remove the international address field
        if general_information_data.get("auditor_country") == "USA":
            general_information_data.pop("auditor_international_address", None)
        # If auditor country is not USA, remove the USA address fields
        elif general_information_data.get("auditor_country") != "USA":
            general_information_data.pop("auditor_address_line_1", None)
            general_information_data.pop("auditor_city", None)
            general_information_data.pop("auditor_state", None)
            general_information_data.pop("auditor_zip", None)
        # Remove unnecessary fields based on audit_period_covered
        # If audit_period_covered is not "other", remove the audit_period_other_months field
        if general_information_data.get("audit_period_covered") != "other":
            general_information_data.pop("audit_period_other_months", None)
        return general_information_data


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
