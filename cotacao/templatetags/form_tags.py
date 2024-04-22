from django import template

register = template.Library()

@register.simple_tag
def get_form_field(form, field_name):
    try:
        # Tenta obter o campo dinamicamente
        return form[field_name]
    except KeyError:
        return ''