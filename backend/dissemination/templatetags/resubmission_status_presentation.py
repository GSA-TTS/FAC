"""
Custom tag to convert the resubmission_status field to a presentable object.
"""

from django import template

from audit.models.constants import RESUBMISSION_STATUS

register = template.Library()


@register.filter()
def resubmission_status_presentation(value=""):
    """
    Given a string, match it to the appropriate resubmission status choice.
    Return an object with the friendly name and tag color.
    If a tag should not exist, returns an empty object.
    """
    value = value.lower()

    match value:
        case RESUBMISSION_STATUS.DEPRECATED:
            # Tag is red on deprecated
            return {
                "friendly_name": "RESUBMITTED",
                "tag_color": "bg-red",  # bg-error-dark
            }
        case RESUBMISSION_STATUS.MOST_RECENT:
            # Tag is green on most recent
            return {
                "friendly_name": "MOST RECENT",
                "tag_color": "bg-green",  # bg-success-dark
            }
        case RESUBMISSION_STATUS.ORIGINAL:
            # No tag on originals
            return {}
        case _:
            # Base case or improper input, no tag
            return {}
