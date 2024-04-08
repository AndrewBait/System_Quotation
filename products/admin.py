from django.contrib import admin
from products.models import Product, Brand, Category, Subcategory, ProductPriceHistory
from cotacao.models import Departamento
from .forms import ProductModelForm
from django.utils.html import format_html
from django.urls import reverse


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1


class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1


class ProductPriceHistoryInline(admin.TabularInline):
    model = ProductPriceHistory
    extra = 1



class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ['nome']
    inlines = [CategoryInline]


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'department']
    list_filter = ['department']
    inlines = [SubcategoryInline]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "department":
            kwargs["queryset"] = Departamento.objects.all().order_by('nome')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    
@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category']
    list_filter = ['category']
    



class ProductAdmin(admin.ModelAdmin):
    form = ProductModelForm
    list_display = ['ean', 'name', 'sku', 'brand', 'department', 'category', 'subcategory', 'status', 'preco_de_custo', 'unidade_de_medida', 'data_de_validade', 'notas']
    list_filter = ['department', 'category', 'subcategory', 'status']
    search_fields = ['name', 'ean']
    fieldsets = (
        (None, {
            'fields': ('name', 'ean', 'sku', 'brand', 'department', 'category', 'subcategory', 'status', 'photo', 'descricao', 'preco_de_custo', 'unidade_de_medida', 'data_de_validade', 'notas')
        }),
    )
    # filter_horizontal = ('fornecedores',)
    # readonly_fields = ['history_link',]

    def history_link(self, obj):
        return format_html('<a href="{}">Histórico</a>', 
            reverse('admin:simple_history_historicalproduct_changelist') + f'?product__id__exact={obj.id}')
    history_link.short_description = 'Histórico de Alterações'




admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)
