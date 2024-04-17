from django import forms
from .models import Cotacao, ItemCotacao, Departamento
from django.core.exceptions import ValidationError
from dal import autocomplete
from products.models import Product


class CotacaoForm(forms.ModelForm):
    class Meta:
        model = Cotacao
        fields = ['nome', 'departamento', 'data_abertura', 'data_fechamento', 'status']
        widgets = {
            'data_abertura': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
            'data_fechamento': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(CotacaoForm, self).__init__(*args, **kwargs)
        self.fields['departamento'].queryset = Departamento.objects.all().order_by('nome')


class ItemCotacaoForm(forms.ModelForm):
    class Meta:
        model = ItemCotacao
        fields = '__all__'
        produto = forms.ModelChoiceField(
            queryset=Product.objects.all(),
            widget=autocomplete.ModelSelect2(url='product-autocomplete')
        )
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_volume': forms.Select(attrs={'class': 'form-control'}),
            'observacao': forms.Textarea(attrs={'cols': 40, 'rows': 2}),        
        }


class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ['nome']
    
    def clean_nome(self):
        nome = self.cleaned_data['nome']
        if Departamento.objects.filter(nome__iexact=nome).exists():
            raise ValidationError("Um departamento com este nome já existe.")
        return nome
    






