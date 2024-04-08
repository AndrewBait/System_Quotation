from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'company', 'email', 'active']
    search_fields = ['name', 'company', 'email']
    list_filter = ['active', 'departments', 'categories', 'subcategories', 'brands']
    filter_horizontal = ['departments', 'categories', 'subcategories', 'brands']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ("Informações Básicas", {
            'fields': ('user', 'name', 'email', 'phone', 'company', 'cnpj', 'active')
        }),
        ("Endereço", {
            'fields': ('address_line_1', 'address_line_2', 'city', 'state', 'zip_code')
        }),
        ("Detalhes Adicionais", {
            'fields': ('minimum_order_value', 'order_response_deadline', 'departments', 'categories', 'subcategories', 'brands')
        }),
    )

    def get_queryset(self, request):
    # Modifica a queryset para excluir soft deleted suppliers
        qs = super().get_queryset(request)
        return qs.filter(deleted=False)  # Certifique-se de que o campo 'deleted' existe
    
    def delete_model(self, request, obj):
        obj.deleted = True
        obj.save()

    def delete_queryset(self, request, queryset):
        queryset.update(deleted=True) 



