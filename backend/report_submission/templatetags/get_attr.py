from django import template

register = template.Library()


class GetAttrNode(template.Node):
    def __init__(self, attr_name):
        self.attr_name = attr_name

    def render(self, context):
        try:
            return context[self.attr_name]
        except Exception:
            return ""


def get_attr(parser, token):
    return GetAttrNode(token).render(parser)


register.filter("get_attr", get_attr)
