from django import forms
from products.models import Product


class ProductModelForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'status': forms.Select(choices=[(True, 'Ativo'), (False, 'Inativo')]),
        }
        
    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            if photo.size > 10*1024*1024:  # 10MB
                raise forms.ValidationError("A imagem não pode ser maior que 10MB.")
            if not photo.name.endswith(('.png', '.jpg', '.jpeg')):
                raise forms.ValidationError("Apenas formatos PNG, JPG são permitidos.")
        return photo


class ProductImportForm(forms.Form):
    file = forms.FileField(label='Selecione um arquivo CSV/XML')