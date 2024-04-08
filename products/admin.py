from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from dal import autocomplete
from django_select2.forms import ModelSelect2Widget
from products.models import Product, Brand, Category, Subcategory, ProductPriceHistory, ProductLine
from cotacao.models import Departamento
from .forms import ProductModelForm


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1


class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1


class ProductPriceHistoryInline(admin.TabularInline):
    model = ProductPriceHistory
    extra = 1


class ProductLineAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Exibir apenas o nome do product line na lista
    search_fields = ('name',)

class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    inlines = [CategoryInline]


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_per_page = 15


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'department']
    list_filter = ['department']
    inlines = [SubcategoryInline]
    search_fields = ['name', 'category']
    list_per_page = 15

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "department":
            kwargs["queryset"] = Departamento.objects.all().order_by('nome')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'subcategory']
    list_per_page = 15


class ProductAdmin(admin.ModelAdmin):
    form = ProductModelForm
    list_display = ('name', 'ean', 'sku', 'brand', 'product_line', 'department', 'category', 'subcategory', 'status')
    list_filter = ('department', 'category', 'subcategory', 'status')
    search_fields = ['name', 'ean']
    fieldsets = (
        (None, {
            'fields': ('name', 'ean', 'sku', 'brand', 'product_line', 'department', 'category', 'subcategory', 'status')
        }),
        ('Detalhes adicionais', {
            'fields': ('photo', 'notas', 'descricao', 'preco_de_custo', 'unidade_de_medida', 'data_de_validade')
        }),
    )
    list_per_page = 15

    def history_link(self, obj):
        return format_html('<a href="{}">Histórico</a>', 
            reverse('admin:simple_history_historicalproduct_changelist') + f'?product__id__exact={obj.id}')
    history_link.short_description = 'Histórico de Alterações'

    def get_list_filter(self, request):
        return ['department', 'category', 'subcategory', 'status']


admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Subcategory, SubcategoryAdmin)
admin.site.register(ProductLine, ProductLineAdmin)