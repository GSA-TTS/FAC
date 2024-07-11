from ..exception_utils import DataMigrationError
from .xform_string_to_string import string_to_string
from django.conf import settings


def xform_remove_hyphen_and_pad_zip(zip):
    """
    Transform a ZIP code string by removing hyphen if present and adding a leading zero when necessary.
    - If the ZIP is settings.GSA_MIGRATION, return it
    - If the ZIP code has hyphen, remove that character.
    - If the ZIP code has 4 or 8 digits, pads with a leading zero.
    - Returns the ZIP code if it has 5 digits or 9 digitis (after padding if needed).
    - Raises an error for other cases.
    """
    # Transformation to be documented.

    if zip == settings.GSA_MIGRATION:
        return zip

    strzip = string_to_string(zip)
    if "-" in strzip:
        parts = strzip.split("-")
        if len(parts[1]) == 4:  # Check if there are exactly four digits after hyphen
            strzip = "".join(parts)
        else:
            raise DataMigrationError(
                f"Zip code {strzip} is malformed.",
                "invalid_zip",
            )

    if len(strzip) in [4, 8]:
        strzip = "0" + strzip
    if len(strzip) == 5 or len(strzip) == 9:
        return strzip
    else:
        raise DataMigrationError(
            f"Zip code {strzip} is malformed.",
            "invalid_zip",
        )
