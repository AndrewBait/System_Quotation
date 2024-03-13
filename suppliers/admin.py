from django.contrib import admin
from suppliers.models import Supplier


class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'company',)
    search_fields = ('name','company',)


admin.site.register(Supplier, SupplierAdmin)

