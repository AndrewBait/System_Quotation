from django import forms
from .models import Departamento, Category, Subcategory, Brand, Supplier
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
            'departments': forms.CheckboxSelectMultiple(),
            'categories': forms.CheckboxSelectMultiple(),
            'subcategories': forms.CheckboxSelectMultiple(),
            'brands': forms.CheckboxSelectMultiple(),

        }
        exclude = ['deleted']  # Exclui o campo 'deleted' do formulário

    def clean_minimum_order_value(self):
        value = self.cleaned_data['minimum_order_value']
        if value < 0:
            raise ValidationError(('Valor inválido. Deve ser maior ou igual a zero.'))
        return value    
    
class SupplierStatusFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('', 'Todos'),
        (True, 'Ativo'),
        (False, 'Inativo'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label='Status', widget=forms.Select(attrs={'onchange': 'this.form.submit();'}))


class SupplierFilterForm(forms.Form):
    STATUS_CHOICES = [('', 'Todos'), ('True', 'Ativo'), ('False', 'Inativo')]
    active = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label='Status', widget=forms.Select(attrs={'onchange': 'this.form.submit();', 'class': 'form-select'}))
    department = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False, label='Departamento', widget=forms.Select(attrs={'onchange': 'this.form.submit();', 'class': 'form-select'}))
    category = forms.ModelChoiceField(queryset=Category.objects.none(), required=False, label='Categoria', widget=forms.Select(attrs={'class': 'form-select'}))
    subcategory = forms.ModelChoiceField(queryset=Subcategory.objects.none(), required=False, label='Subcategoria', widget=forms.Select(attrs={'class': 'form-select'}))
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(), required=False, label='Marca', widget=forms.Select(attrs={'onchange': 'this.form.submit();', 'class': 'form-select'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['category'].queryset = Category.objects.filter(department_id=department_id).order_by('name')
                if 'category' in self.data:
                    category_id = int(self.data.get('category'))
                    self.fields['subcategory'].queryset = Subcategory.objects.filter(category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input; ignore and fallback to empty City queryset