from django import template

register = template.Library()

@register.filter(name='badge_class')
def badge_class(value):
    classes = {
        'Aberto': 'bg-success',
        'Fechado': 'bg-danger',
        'Pendente': 'bg-warning',
        'Em progresso': 'bg-info',
        # Adicione outros status conforme necessário
    }
    return classes.get(value, 'bg-secondary')  # 'bg-secondary' é um fallback padrão
