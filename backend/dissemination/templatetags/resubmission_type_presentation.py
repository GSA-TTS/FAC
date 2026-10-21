"""
Custom tag to convert the resubmission_type field to a presentable object.
"""

from django import template

from audit.models.constants import RESUBMISSION_TYPE

register = template.Library()


@register.filter()
def resubmission_type_presentation(value=""):
    """
    Given a string, match it to the appropriate resubmission type choice.
    Return an object with the friendly name.
    If a tag should not exist, returns an empty object.
    """
    value = value.lower()

    match value:
        case RESUBMISSION_TYPE.AUDIT_PDF:
            return {
                "friendly_name": "Material",
            }
        case RESUBMISSION_TYPE.NON_MATERIAL_PDF:
            return {
                "friendly_name": "Non-Material",
            }
        case RESUBMISSION_TYPE.SFSAC_ONLY:
            return {
                "friendly_name": "SF-SAC",
            }
        case _:
            # Base case or improper input
            return {}
