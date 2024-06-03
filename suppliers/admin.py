from django.contrib import admin
from .models import Supplier
from django import forms
from django.forms.widgets import CheckboxSelectMultiple

class SupplierAdminForm(forms.ModelForm):
    delivery_days = forms.MultipleChoiceField(
        choices=[
            ("SEG", "Segunda-feira"),
            ("TER", "Terça-feira"),
            ("QUA", "Quarta-feira"),
            ("QUI", "Quinta-feira"),
            ("SEX", "Sexta-feira"),
            ("SAB", "Sábado"),
            ("DOM", "Domingo")
        ],
        widget=CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = Supplier
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['delivery_days'].initial = self.instance.delivery_days.split(',') if self.instance.delivery_days else []

    def clean_delivery_days(self):
        delivery_days = self.cleaned_data.get('delivery_days')
        if delivery_days:
            return ','.join(delivery_days)
        return ''

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    form = SupplierAdminForm
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
        ("Dias de Entrega e Prazo de Faturamento", {
            'fields': ('delivery_days', 'billing_deadline', 'specific_billing_deadline')
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(deleted=False)

    def delete_model(self, request, obj):
        obj.deleted = True
        obj.save()

    def delete_queryset(self, request, queryset):
        queryset.update(deleted=True)
