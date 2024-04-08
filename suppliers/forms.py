from django import forms
from .models import Supplier, Departamento, Category, Brand
from django.core.exceptions import ValidationError




class SupplierForm(forms.ModelForm):
    
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
            'minimum_order_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01' ,'placeholder': '0.000,00'}),
            'order_response_deadline': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),

        }
        exclude = ['deleted']  # Exclui o campo 'deleted' do formulário

    def clean_minimum_order_value(self):
        value = self.cleaned_data['minimum_order_value']
        if value < 0:
            raise ValidationError(('Valor inválido. Deve ser maior ou igual a zero.'))
        return value    


class SupplierFilterForm(forms.Form):
    active = forms.ChoiceField(choices=[('', 'Todos'), (True, 'Ativo'), (False, 'Inativo')], required=False, label='Status')
    department = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False, label='Departamento')
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, label='Categoria')
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(), required=False, label='Marca')