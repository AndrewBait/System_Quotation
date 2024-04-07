from django import forms
from .models import Supplier


class SupplierForm(forms.ModelForm):
    cep = forms.CharField(max_length=9, required=False, label='CEP')

    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'company', 'email', 'cnpj', 'cep']
