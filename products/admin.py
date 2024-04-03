from django.contrib import admin
from products.models import Product, Brand, Category, Subcategory
from cotacao.models import Departamento
from .forms import ProductModelForm


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ProductAdmin(admin.ModelAdmin):
    form = ProductModelForm
    list_display = ('ean','name', 'brand',)
    search_fields = ('name',)


class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1


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



# admin.site.register(Category, CategoryAdmin)
# admin.site.register(Subcategory)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)
