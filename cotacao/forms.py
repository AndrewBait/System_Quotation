from django import forms
from .models import Cotacao, ItemCotacao

class CotacaoForm(forms.ModelForm):
    class Meta:
        model = Cotacao
        fields = ['nome', 'departamento', 'data_abertura', 'data_fechamento']
        widgets = {
            'data_abertura': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
            'data_fechamento': forms.DateInput(format=('%Y-%m-%d'), attrs={'type': 'date'}),
        }

class ItemCotacaoForm(forms.ModelForm):
    class Meta:
        model = ItemCotacao
        fields = ['produto', 'quantidade', 'tipo_volume']
        widgets = {
            'produto': forms.Select(attrs={'class': 'form-control'}),
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'tipo_volume': forms.Select(attrs={'class': 'form-control'}),
        }
