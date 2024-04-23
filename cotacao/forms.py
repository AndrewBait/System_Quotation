from django import forms
from .models import Cotacao, ItemCotacao, Departamento
from django.core.exceptions import ValidationError
from dal import autocomplete
from products.models import Product
from suppliers.models import Supplier
from django_select2 import forms as s2forms
from .models import RespostaCotacao


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
    fornecedores = forms.ModelMultipleChoiceField(
        queryset=Supplier.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )


class RespostaCotacaoForm(forms.ModelForm):
    class Meta:
        model = RespostaCotacao
        fields = ['cotacao', 'fornecedor']  # Adicione outros campos se necessário
        
    
    def clean(self):
        cleaned_data = super().clean()
        precos_fornecidos = any(
            value for key, value in cleaned_data.items() if key.startswith('preco_')
        )
        if not precos_fornecidos:
            raise forms.ValidationError("Forneça pelo menos um preço para responder à cotação.")
        return cleaned_data
    

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cotacao'].widget = forms.HiddenInput()
        self.fields['fornecedor'].widget = forms.HiddenInput()

        # Adicionar campos para cada item da cotação
        for item in self.instance.cotacao.itens_cotacao.all():
            self.fields[f'preco_{item.id}'] = forms.DecimalField(
                label=f'Preço para {item.produto.name}',
                max_digits=10, decimal_places=2, required=False
            )
            self.fields[f'observacao_{item.id}'] = forms.CharField(
                label='Observação', max_length=100, required=False,
                widget=forms.TextInput(attrs={'placeholder': 'Observação opcional'})
            )
