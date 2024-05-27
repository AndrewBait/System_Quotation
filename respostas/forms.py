from django import forms
from .models import RespostaCotacao, ItemRespostaCotacao
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from django.forms import TextInput, NumberInput, FileInput
from django.forms import inlineformset_factory
from .models import PedidoAgrupado, Pedido
import bleach
import re


class ItemRespostaForm(forms.ModelForm):
    class Meta:
        model = ItemRespostaCotacao
        fields = ['preco', 'prazo', 'preco_prazo_alternativo', 'prazo_alternativo', 'observacao', 'imagem']
        widgets = {
            'preco': NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.001'}),
            'prazo': NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '1'}),
            'preco_prazo_alternativo': NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.001'}),
            'prazo_alternativo': forms.Select(choices=[
                (None, 'Selecione um prazo alternativo'),
                (0, 'À vista'),
                (7, '7 dias'),
                (14, '14 dias'),
                (21, '21 dias'),
                (28, '28 dias'),
            ], attrs={'class': 'form-control'}),
            'observacao': TextInput(attrs={'class': 'form-control', 'maxlength': '144'}),
            'imagem': FileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
        }

    def __init__(self, *args, **kwargs):
        self.item_cotacao = kwargs.pop('item_cotacao', None)
        super(ItemRespostaForm, self).__init__(*args, **kwargs)
        self.fields['imagem'].required = False


        
    def clean_preco(self):
        preco = self.cleaned_data.get('preco')
        if preco:
            try:
                preco_dec = Decimal(preco)
                if preco_dec < 0:
                    raise ValidationError('O preço não pode ser negativo.')
                if not re.match(r'^\d+\.\d{3}$', str(preco_dec)):
                    raise ValidationError('O preço deve ter três casas decimais.')
                return preco_dec
            except InvalidOperation:
                raise ValidationError('Formato de preço inválido.')
        return preco
    
    
    def clean_observacao(self):
        observacao = self.cleaned_data.get('observacao')
        if observacao:
            clean_observacao = bleach.clean(observacao)
            return clean_observacao
        return observacao
    

    
    def clean_imagem(self):
        imagem = self.cleaned_data.get('imagem')
        if imagem:
            if hasattr(imagem, 'content_type'):
                if not imagem.content_type.startswith('image/'):
                    raise ValidationError('Apenas arquivos de imagem são permitidos.')
            return imagem
        return None
        
    @property
    def ean(self):
        return self.item_cotacao.produto.ean

    @property
    def quantidade(self):
        return self.item_cotacao.quantidade

    @property
    def tipo_volume_display(self):
        return self.item_cotacao.get_tipo_volume_display()

    @property
    def produto_nome(self):
        return self.item_cotacao.produto.name

    @property
    def observacao_item(self):
        return self.item_cotacao.observacao
    
    
    def clean_preco(self):
        preco = self.cleaned_data.get('preco')
        if preco:
            try:
                preco_dec = Decimal(preco)
                # Verifica se o valor é negativo
                if preco_dec < 0:
                    raise ValidationError('O preço não pode ser negativo.')
                # Verifica se possui exatamente três casas decimais
                if not re.match(r'^\d+\.\d{3}$', str(preco_dec)):
                    raise ValidationError('O preço deve ter três casas decimais.')
                return preco_dec
            except InvalidOperation:
                raise ValidationError('Formato de preço inválido.')
        return preco   

    

    def get_item_data(self, field):
        # Esta função pode ser usada para acessar dados seguros do ItemCotacao associado
        return getattr(self.item_cotacao, field, None)

class RespostaCotacaoForm(forms.ModelForm):
    class Meta:
        model = RespostaCotacao
        fields = ['prazo_alternativo']  # Inclui o campo prazo_alternativo

    def __init__(self, *args, **kwargs):
        self.cotacao = kwargs.pop('cotacao', None)
        super(RespostaCotacaoForm, self).__init__(*args, **kwargs)
        if self.cotacao:
            self.item_forms = []
            for item in self.cotacao.itens_cotacao.all():
                item_form = ItemRespostaForm(prefix=f'item_{item.pk}', instance=ItemRespostaCotacao(item_cotacao=item), item_cotacao=item)
                self.item_forms.append(item_form)

    def save(self, commit=True):
        resposta = super().save(commit=False)
        if commit:
            resposta.save()
            for item_form in self.item_forms:
                item_resposta = item_form.save(commit=False)
                item_resposta.resposta_cotacao = resposta
                item_resposta.save()
        return resposta


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['quantidade', 'preco', 'produto']

PedidoFormSet = inlineformset_factory(PedidoAgrupado, Pedido, form=PedidoForm, extra=0)