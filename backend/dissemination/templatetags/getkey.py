"""
Custom tag to pull a key with a space out of a dictionary.
Example:
{{ data.'Notes to SEFA' }} does not work.
Instead, {{ data|getkey:"Notes to SEFA" }}
"""
from django import template

register = template.Library()


@register.filter(name="getkey")
def getkey(value, arg):
    return value.get(arg, [])
