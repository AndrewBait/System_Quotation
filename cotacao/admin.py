from django.contrib import admin
from .models import Departamento, Cotacao, ItemCotacao

class ItemCotacaoInline(admin.TabularInline):
    model = ItemCotacao
    extra = 1  # Define quantos campos para novos itens devem ser mostrados por padrão


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['nome']

@admin.register(Cotacao)
class CotacaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'departamento', 'data_abertura', 'data_fechamento']
    list_filter = ['departamento', 'data_abertura', 'data_fechamento']
    search_fields = ['nome', 'departamento__nome']
    date_hierarchy = 'data_abertura'
    inlines = [ItemCotacaoInline] 
