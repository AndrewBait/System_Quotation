from django.contrib import admin
from .models import Departamento, Cotacao, ItemCotacao
from django.http import HttpResponse
from products.models import Product, Departamento
from .forms import ItemCotacaoForm
import csv


class ItemCotacaoInline(admin.TabularInline):
    model = ItemCotacao
    form = ItemCotacaoForm
    extra = 0
    

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'ean']
    search_fields = ['name', 'sku', 'ean']    



@admin.register(Departamento) 
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    search_fields = ['nome']
    

def mudar_status_para_inativo(modeladmin, request, queryset):
    queryset.update(status='inativo')
mudar_status_para_inativo.short_description = "Marcar selecionados como inativo"


@admin.register(Cotacao) 
class CotacaoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'departamento', 'data_abertura', 'data_fechamento', 'status', 'total_itens']
    list_filter = ['departamento', 'status', 'data_abertura', 'data_fechamento' ]
    search_fields = ['nome', 'departamento__nome']
    date_hierarchy = 'data_abertura'
    inlines = [ItemCotacaoInline] 
    actions = ['tornar_inativo', 'tornar_ativo', 'exportar_para_csv']
    list_per_page = 20
    
    def tornar_inativo(self, request, queryset):
        queryset.update(status='inativo')
    tornar_inativo.short_description = "Marcar como inativo"

    def tornar_ativo(self, request, queryset):
        queryset.update(status='ativo')
    tornar_ativo.short_description = "Marcar como ativo"
    
    def total_itens(self, obj):
        return obj.itens_cotacao.count()
    total_itens.short_description = 'Total de Itens'
    
    def exportar_para_csv(self, request, queryset):

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="cotacoes.csv"'
        writer = csv.writer(response)
        writer.writerow(['Nome', 'Departamento', 'Data Abertura', 'Data Fechamento', 'Status'])
        for cotacao in queryset:
            writer.writerow([cotacao.nome, cotacao.departamento.nome if cotacao.departamento else "", cotacao.data_abertura, cotacao.data_fechamento, cotacao.status])
        return response
    exportar_para_csv.short_description = "Exportar para CSV"
    



    