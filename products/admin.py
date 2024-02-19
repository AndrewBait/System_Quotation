from django.contrib import admin
from products.models import Product, Brand


class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('ean','name', 'brand',)
    search_fields = ('name',)


admin.site.register(Brand, BrandAdmin)
admin.site.register(Product, ProductAdmin)