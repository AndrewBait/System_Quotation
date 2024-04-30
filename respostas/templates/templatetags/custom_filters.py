from django import template

register = template.Library()

@register.filter(name='get_attribute')
def get_attribute(value, arg):
    """
    Generic attribute getter filter.
    """
    return getattr(value, arg, None)