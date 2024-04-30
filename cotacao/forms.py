from django import forms
from .models import Cotacao, ItemCotacao, Departamento
from django.core.exceptions import ValidationError
from dal import autocomplete
from products.models import Product
from suppliers.models import Supplier
from django_select2 import forms as s2forms
import logging

logger = logging.getLogger(__name__)


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
    produto = s2forms.ModelSelect2Widget(
        model=Product,
        search_fields=['name__icontains', 'sku__icontains', 'ean__icontains'],
    )
    class Meta:
        model = ItemCotacao
        fields = ['produto','quantidade', 'tipo_volume', 'observacao']

    def __init__(self, *args, **kwargs):
        super(ItemCotacaoForm, self).__init__(*args, **kwargs)
        self.fields['produto'].widget.attrs.update({'class': 'form-control'})
        self.fields['quantidade'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_volume'].widget.attrs.update({'class': 'form-control'})
        self.fields['observacao'].widget.attrs.update({'class': 'form-control'})



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
    fornecedores = forms.ModelMultipleChoiceField( # Campo para selecionar fornecedores
        queryset=Supplier.objects.all(), # Obtendo todos os fornecedores
        widget=forms.CheckboxSelectMultiple, # Utilizando um widget de seleção de múltipla escolha
        required=True # O campo é obrigatório
    )


# class RespostaCotacaoForm(forms.ModelForm):
#     class Meta:
#         model = RespostaCotacao
#         exclude = []

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if self.instance and hasattr(self.instance, 'cotacao'):
#             itens_cotacao = self.instance.cotacao.itens_cotacao.all()
#             for item in itens_cotacao:
#                 self.fields[f'preco_{item.id}'] = forms.DecimalField(
#                     required=False,
#                     max_digits=10,
#                     decimal_places=3,
#                     help_text='Insira o preço com até três casas decimais.'
#                 )
#                 self.fields[f'observacao_{item.id}'] = forms.CharField(
#                     max_length=100,
#                     required=False,
#                     widget=forms.Textarea(attrs={'rows': 1})
#                 )

#     def save(self, commit=True):
#         resposta_cotacao = super().save(commit=False)
#         if commit:
#             resposta_cotacao.save()
#             self.save_m2m()

#             for item in resposta_cotacao.cotacao.itens_cotacao.all():
#                 preco_field = f'preco_{item.id}'
#                 observacao_field = f'observacao_{item.id}'
#                 preco = self.cleaned_data.get(preco_field)
#                 observacao = self.cleaned_data.get(observacao_field, "")
#                 logger.debug(f"Saving item {item.id}: Price - {preco}, Observation - {observacao}")

#                 obj, created = ItemRespostaCotacao.objects.update_or_create(
#                     resposta_cotacao=resposta_cotacao,
#                     item_cotacao=item,
#                     defaults={'preco': preco, 'observacao': observacao}
#                 )
#                 logger.debug(f"Item {'created' if created else 'updated'}: {obj.id}")
#                 logger.debug(f"Received price {preco} for item {item.id}")
#         return resposta_cotacao

