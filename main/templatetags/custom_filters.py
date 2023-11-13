from django import template

register = template.Library()

@register.filter
def add_commas(value):
    try:
        return '{:,.0f}'.format(float(value))
    except (ValueError, TypeError):
        return value
