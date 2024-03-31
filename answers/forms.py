from django import forms
from .models import Answer



class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['price']
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class AnswerItemForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['price']
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class NonAuthenticatedAnswerForm(forms.ModelForm):
    fornecedor_email = forms.EmailField(label="Seu E-mail", required=True)

    class Meta:
        model = Answer
        fields = ['price']
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }

# Função para criar o formulário dinamicamente baseado nos itens
def create_answer_formset(cotacao, data=None):
    item_forms = []
    for item in cotacao.itens_cotacao.all():
        class DynamicAnswerForm(NonAuthenticatedAnswerForm):
            class Meta(NonAuthenticatedAnswerForm.Meta):
                fields = ['price', 'fornecedor_email']

        form_prefix = f"item_{item.id}"
        item_forms.append(DynamicAnswerForm(prefix=form_prefix, data=data))
    return item_forms