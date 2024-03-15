from django import forms
from .models import Cotation, CotationProduct, VolumeType


class CotationForm(forms.ModelForm):
    class Meta:
        model = Cotation
        fields = ['nome', 'data_abertura', 'data_fechamento']
        widgets = {
            'data_abertura': forms.DateInput(format=('%Y-%m-%d'), attrs={'class':'form-control', 'placeholder':'Selecione uma data', 'type':'date'}),
            'data_fechamento': forms.DateInput(format=('%Y-%m-%d'), attrs={'class':'form-control', 'placeholder':'Selecione uma data', 'type':'date'}),
        }


class CotationProductForm(forms.ModelForm):
    class Meta:
        model = CotationProduct
        fields = ['product', 'quantidade', 'tipo_volume', 'preco_7_dias', 'preco_14_dias', 'preco_21_dias', 'preco_28_dias', 'observacao']
        widgets = {
            'tipo_volume': forms.Select(),
            'observacao': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super(CotationProductForm, self).__init__(*args, **kwargs)
        self.fields['tipo_volume'].queryset = VolumeType.objects.all()
# Para os produtos, considere usar formsets do Django
