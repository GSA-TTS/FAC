from django.conf import settings
from .xform_string_to_string import string_to_string


def xform_retrieve_uei(uei):
    """Returns the stripped UEI if it exists, otherwise returns `GSA_MIGRATION`."""
    # Transformation to be documented.
    str_uei = string_to_string(uei)
    if not str_uei:
        return settings.GSA_MIGRATION

    return str_uei
