from django import forms
from .models import RespostaCotacao, ItemRespostaCotacao, ItemCotacao
import bleach


class ItemRespostaForm(forms.ModelForm):
    class Meta:
        model = ItemRespostaCotacao
        fields = ['preco', 'observacao']
    
    def __init__(self, *args, **kwargs):
        self.item_cotacao = kwargs.pop('item_cotacao', None)
        super(ItemRespostaForm, self).__init__(*args, **kwargs)
    
    
    def clean_observacao(self):
        observacao = self.cleaned_data.get('observacao')
        # Sanitize the observation field to prevent XSS
        clean_observacao = bleach.clean(observacao)
        return clean_observacao
        
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