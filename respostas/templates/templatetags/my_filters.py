from django import template

register = template.Library()

@register.filter
def average(queryset, field_name):
    total = 0
    count = 0
    for item in queryset:
        value = getattr(item, field_name)
        if value is not None:
            total += value
            count += 1
    return total / count if count else None