from django import forms
from .models import Cotation, CotationProduct

class CotationForm(forms.ModelForm):
    class Meta:
        model = Cotation
        fields = ['nome', 'data_abertura', 'data_fechamento', 'observacao']

# Para os produtos, considere usar formsets do Django
