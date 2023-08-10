"""
Custom tag to filter underscores out of strings and capitalize the first character.
Example: "report_id" to "Report id"
"""
from django import template

register = template.Library()

@register.filter()
def field_name_to_label(value):
    value = value.replace('_', ' ')
    return value.title()