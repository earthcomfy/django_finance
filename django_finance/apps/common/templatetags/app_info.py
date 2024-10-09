from django import template

register = template.Library()


@register.simple_tag
def app_name():
    return "FinTrack"


@register.simple_tag
def app_description():
    return "Personal Finance Management App with Django, HTMX, Alpine, Tailwind and Plaid"
