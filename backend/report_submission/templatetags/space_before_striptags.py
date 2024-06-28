"""
Custom tag to add spaces between list items when using `striptags`.
Example:
"<li>An error.</li><li>Another error.</li>"
"An error. Another error."
"""

from django import template
from django.utils.html import strip_tags

register = template.Library()


@register.filter(name="space_before_striptags")
def space_before_striptags(value):
    result = str(value)

    result = result.replace("<li>", " ")
    result = strip_tags(result)
    result = result.strip()

    return result
