from django import template

register = template.Library()


@register.simple_tag
def app_name():
    return "FinTrack"
