from django import forms
from products.models import Product


class ProductModelForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'    


class ProductImportForm(forms.Form):
    file = forms.FileField(label='Selecione um arquivo CSV/XML')