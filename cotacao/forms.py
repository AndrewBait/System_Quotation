from django import forms
from .models import Cotacao, ItemCotacao, Departamento
from django.core.exceptions import ValidationError
from dal import autocomplete
from products.models import Product
from suppliers.models import Supplier


class CotacaoForm(forms.ModelForm):
    class Meta:
        model = Cotacao
        fields = ['nome', 'departamento', 'data_abertura', 'data_fechamento', 'status', 'prazo']
        widgets = {
            'data_abertura': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
            'data_fechamento': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
            'prazo': forms.Select()  # Adicionando um widget de seleção para o prazo
        }
        
    def __init__(self, *args, **kwargs):
        super(CotacaoForm, self).__init__(*args, **kwargs)
        self.fields['departamento'].queryset = Departamento.objects.all().order_by('nome')


class ItemCotacaoForm(forms.ModelForm):
    produto = forms.ModelChoiceField(
        queryset=Product.objects.all(),
        widget=autocomplete.ModelSelect2(url='cotacao:product-autocomplete'),
        label="Produto"
    )


    class Meta:
        model = ItemCotacao
        fields = ['produto', 'quantidade', 'tipo_volume', 'observacao']


class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ['nome']
    
    def clean_nome(self):
        nome = self.cleaned_data['nome']
        if Departamento.objects.filter(nome__iexact=nome).exists():
            raise ValidationError("Um departamento com este nome já existe.")
        return nome
    
    
class EnviarCotacaoForm(forms.Form):
    fornecedores = forms.ModelMultipleChoiceField(
        queryset=Supplier.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )





