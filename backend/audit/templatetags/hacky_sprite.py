"""
Custom tag to support simpler writing of USWDS sprite icon references.
"""
from django import template

register = template.Library()


@register.inclusion_tag("uswds_sprite.html")
def uswds_sprite(icon_name):
    return {"icon_name": icon_name}
