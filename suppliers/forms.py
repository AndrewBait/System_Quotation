from django import forms
from .models import Supplier


class SupplierForm(forms.ModelForm):
    cep = forms.CharField(max_length=9, required=False, label='CEP')

    class Meta:
        model = Supplier
        fields = '__all__'  # Inclui todos os campos do modelo no formulário
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'minimum_order_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.000,00'}),
            'order_response_deadline': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'departments': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'subcategories': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'brands': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        exclude = ['deleted']  # Exclui o campo 'deleted' do formulário
