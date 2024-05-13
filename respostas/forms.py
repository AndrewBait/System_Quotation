from django import forms
from .models import RespostaCotacao, ItemRespostaCotacao
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from django.forms import TextInput, NumberInput, FileInput
import bleach
import re


class ItemRespostaForm(forms.ModelForm):
    class Meta:
        model = ItemRespostaCotacao
        fields = ['preco', 'observacao', 'imagem']
        widgets = {
            'preco': NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.001'}),
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
        return observacao  # Retorna None se não houver observação
    

    
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
        fields = [] # Não precisamos de campos aqui, pois a relação com a cotação e o fornecedor será definida na view

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