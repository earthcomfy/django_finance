import re

from django import template

register = template.Library()


@register.filter()
def human_readable_category(category):
    return re.sub(r"_", " ", category).title().replace("And", "and").replace("Or", "or")
