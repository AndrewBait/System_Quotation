from django import forms
from products.models import Product, Category, Subcategory
from cotacao.models import Departamento  
from dal import autocomplete
from dal import autocomplete


class ProductModelForm(forms.ModelForm):
    department = forms.ModelChoiceField(queryset=Departamento.objects.all().order_by('nome'), required=True, label="Departamento")

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'status': forms.Select(choices=[(True, 'Ativo'), (False, 'Inativo')]),
            'department': autocomplete.ModelSelect2(url='products:department-autocomplete'),
            'category': autocomplete.ModelSelect2(url='products:category-autocomplete',
                                                  forward=['department']),
            'subcategory': autocomplete.ModelSelect2(url='products:subcategory-autocomplete',
                                                     forward=['category']),
        }

    def __init__(self, *args, **kwargs):
        super(ProductModelForm, self).__init__(*args, **kwargs)
        # Inicializa os campos de categoria e subcategoria vazios
        self.fields['category'].queryset = Category.objects.none()
        self.fields['subcategory'].queryset = Subcategory.objects.none()

        # Atualiza a queryset de categorias e subcategorias quando um departamento é selecionado
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['category'].queryset = Category.objects.filter(department_id=department_id).order_by('name')
                category_id = int(self.data.get('category'))
                self.fields['subcategory'].queryset = Subcategory.objects.filter(category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Caso inválido, não atualiza as querysets


class ProductImportForm(forms.Form):
    file = forms.FileField(label='Selecione um arquivo CSV/XML')