from django import forms
from products.models import Product, Category, Subcategory, Brand, Embalagem
from cotacao.models import Departamento  
from dal import autocomplete
from django_select2.forms import ModelSelect2Widget


class ProductModelForm(forms.ModelForm):
    altura_embalagem = forms.FloatField(label='Altura', required=False)
    largura_embalagem = forms.FloatField(label='Largura', required=False)
    comprimento_embalagem = forms.FloatField(label='Comprimento', required=False)
    espessura_embalagem = forms.FloatField(label='Espessura', required=False)
    raio_embalagem = forms.FloatField(label='Raio', required=False)
    UNIDADE_CHOICES = (
        ('mm', 'Milímetro'),
        ('cm', 'Centímetro'),
        ('m', 'Metro'),
    )
    unidade_dimensao = forms.ChoiceField(label='Unidade de Medida', choices=UNIDADE_CHOICES, required=False)
    department = forms.ModelChoiceField(queryset=Departamento.objects.all().order_by('nome'), required=True, label="Departamento")
    widget=autocomplete.ModelSelect2(url='products:department-autocomplete')
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        required=False,
        label='Marca',
        # widget=ModelSelect2Widget(
        #     url='products:brands-autocomplete',
        #     model=Brand,
        #     search_fields=['name__icontains'],
        #     attrs={'data-minimum-input-length': 2},  # O usuário deve digitar pelo menos 3 caracteres antes de iniciar a busca
        #     # Aqui você define a URL configurada para a busca autocomplete
        #     data_url='/products/list-brands/'

        )
    
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'brand': autocomplete.ModelSelect2(url='products:brands-autocomplete'),
            'descricao': forms.Textarea(attrs={'rows': 5, 'cols': 40}),
            'notas': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
            'status': forms.Select(choices=[(True, 'Ativo'), (False, 'Inativo')]),
            'category': autocomplete.ModelSelect2(url='products:category-autocomplete', forward=['department']),
            'subcategory': autocomplete.ModelSelect2(url='products:subcategory-autocomplete', forward=['category']),
            'subcategory': autocomplete.ModelSelect2(url='products:subcategory-autocomplete', forward=['category']),
        }

    def save(self, commit=True):
        product = super().save(commit=False)
        altura_embalagem = self.cleaned_data.get('altura_embalagem')
        largura_embalagem = self.cleaned_data.get('largura_embalagem')
        comprimento_embalagem = self.cleaned_data.get('comprimento_embalagem')
        espessura_embalagem = self.cleaned_data.get('espessura_embalagem')
        raio_embalagem = self.cleaned_data.get('raio_embalagem')
        unidade_dimensao = self.cleaned_data.get('unidade_dimensao')

        if altura_embalagem and largura_embalagem and comprimento_embalagem and espessura_embalagem and unidade_dimensao:
            embalagem = Embalagem.objects.create(
                altura=altura_embalagem,
                largura=largura_embalagem,
                comprimento=comprimento_embalagem,
                espessura=espessura_embalagem,
                raio=raio_embalagem,
                unidade=unidade_dimensao
            )
            embalagem.save()
            product.embalagem = embalagem

        if commit:
            product.save()
        return product        

    def __init__(self, *args, **kwargs):
        super(ProductModelForm, self).__init__(*args, **kwargs)
        self.fields['product_line'].widget.attrs['class'] = 'form-control'  # Adicione classes CSS ao campo se desejar
        # Inicializa as querysets para edição
        if self.instance.pk:
            self.fields['category'].queryset = Category.objects.filter(department=self.instance.department)
            self.fields['subcategory'].queryset = Subcategory.objects.filter(category=self.instance.category)
        else:
            # Inicializa vazias se for um novo produto
            self.fields['category'].queryset = Category.objects.none()
            self.fields['subcategory'].queryset = Subcategory.objects.none()

        # Manipulação dinâmica com base no input do usuário
        if 'department' in self.data:
            try:
                department_id = int(self.data.get('department'))
                self.fields['category'].queryset = Category.objects.filter(department_id=department_id).order_by('name')
                if 'category' in self.data:
                    category_id = int(self.data.get('category'))
                    self.fields['subcategory'].queryset = Subcategory.objects.filter(category_id=category_id).order_by('name')
            except (ValueError, TypeError):
                pass  # Caso inválido, não atualiza as querysets


class ProductImportForm(forms.Form):
    file = forms.FileField(label='Selecione um arquivo CSV/XML')


