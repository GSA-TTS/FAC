from django import template

from django.utils.dateparse import parse_datetime

register = template.Library()


@register.filter(name="parse_date")
def parse_date(value):
    return parse_datetime(value)
