from ..exception_utils import DataMigrationError
from ..transforms.xform_string_to_string import string_to_string


def cognizant_oversight(audit_header):
    """Retrieve cognizant oversight information for a given audit header."""

    cognizant = string_to_string(audit_header.COGAGENCY)
    oversight = string_to_string(audit_header.OVERSIGHTAGENCY)
    if cognizant and len(cognizant) > 2:
        raise DataMigrationError(
            f"Invalid cognizant agency: {cognizant}", "invalid_cognizant"
        )

    return cognizant, oversight
