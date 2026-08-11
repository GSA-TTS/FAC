from django import template
from config import settings
from django.template.defaulttags import register as reg

import logging

logger = logging.getLogger(__name__)

register = template.Library()


@register.simple_tag
def do_DAP():
    return "Y" if settings.DEBUG is not True else "N"


# https://stackoverflow.com/a/8000091
@reg.filter
def KV(dict, key):
    # logger.info(f"Looking up [{key}] in {dict} ")
    return dict.get(key)


@reg.filter
def repl(string, orig_new):
    # logger.info(f"Looking up [{key}] in {dict} ")
    s = orig_new.split("|")
    return string.replace(s[0], s[1])


@register.filter
def get_type(value):
    return type(value)


@register.filter
def split_string(value, char):
    return value.split(char)
