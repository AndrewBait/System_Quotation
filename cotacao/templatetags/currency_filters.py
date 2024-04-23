from django import template
from django.utils.formats import localize

register = template.Library()

@register.filter
def format_currency(value):
    return localize(value)  # Assumindo que 'value' é um DecimalField