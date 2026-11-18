import json
from decimal import Decimal

from django import template
from django.conf import settings
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

SYMBOLS = {'USD': 'US$', 'EUR': '€', 'GBP': '£', 'UGX': 'UGX '}


@register.filter
def money(value, currency='USD'):
    """2850 -> "US$2,850". Blank prices read "Price on request"."""
    if value in (None, ''):
        return 'Price on request'
    value = Decimal(value)
    fmt = '{:,.0f}' if value == value.to_integral() else '{:,.2f}'
    return f'{SYMBOLS.get(currency, currency + " ")}{fmt.format(value)}'


@register.filter
def absolute(path):
    """Make a site-relative URL absolute using the canonical SITE_URL."""
    if not path:
        return ''
    path = str(path)
    if path.startswith(('http://', 'https://')):
        return path
    return settings.SITE_URL + (path if path.startswith('/') else '/' + path)


@register.filter
def jsonld(data):
    """Serialise structured data for a <script type="application/ld+json"> block."""
    text = json.dumps(data, ensure_ascii=False, default=str)
    # Stop "</script>" inside content from closing the tag early.
    text = text.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    return mark_safe(text)


@register.inclusion_tag('components/field.html')
def field(bound_field, span=False, label=None):
    widget = bound_field.field.widget.__class__.__name__
    return {
        'f': bound_field,
        'span': span,
        'label': label or bound_field.label,
        'is_choices': widget in ('CheckboxSelectMultiple', 'RadioSelect'),
        'is_checkbox': widget == 'CheckboxInput',
    }


@register.simple_tag(takes_context=True)
def page_url(context, page_number):
    """Link to another page of a listing, keeping the current filters."""
    params = context['request'].GET.copy()
    params['page'] = page_number
    return '?' + params.urlencode()


@register.simple_tag
def stars(rating):
    rating = int(rating or 0)
    icons = ''.join(
        '<i class="fa-solid fa-star" aria-hidden="true"></i>' if i < rating
        else '<i class="fa-regular fa-star" aria-hidden="true"></i>'
        for i in range(5)
    )
    return format_html('<span class="text-amber-500 text-sm" role="img" aria-label="{} out of 5 stars">{}</span>',
                       rating, mark_safe(icons))
