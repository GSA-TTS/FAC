from django import template
from config import settings


register = template.Library()


@register.simple_tag
def do_DAP():
    return "Y" if settings.DEBUG is not True else "N"
