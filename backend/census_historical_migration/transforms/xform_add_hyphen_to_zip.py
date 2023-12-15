from ..exception_utils import DataMigrationError
from .xform_string_to_string import string_to_string


def xform_add_hyphen_to_zip(zip):
    """
    Transform a ZIP code string by adding a leading zero and a hyphen when applicable.
    - If the ZIP code has 4 or 8 digits, pads with a leading zero.
    - If the ZIP code has 9 digits (after padding if needed), inserts a hyphen after the fifth digit.
    - Returns the original ZIP code if it has 5 digits.
    - Raises an error for other cases.
    """
    strzip = string_to_string(zip)

    if len(strzip) in [4, 8]:
        # FIXME - MSHD: Record this transformation if len == 4.
        strzip = "0" + strzip
    if len(strzip) == 5:
        return strzip
    elif len(strzip) == 9:
        # FIXME - MSHD: Record this transformation.
        return f"{strzip[0:5]}-{strzip[5:9]}"
    else:
        raise DataMigrationError("Zip code is malformed.")
