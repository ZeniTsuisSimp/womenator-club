from django import template

register = template.Library()


@register.filter
def split(value, sep=', '):
    if not value:
        return []
    return value.split(sep)
