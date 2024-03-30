from django import forms
from django.contrib.auth.models import User
from .models import Supplier


class SupplierForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Senha")
    
    class Meta:
        model = Supplier
        fields = ['name', 'phone', 'company', 'email', 'cnpj']

    def save(self, commit=True):
        # Certifique-se de chamar clean() para assegurar que cleaned_data esteja disponível
        self.full_clean()
        supplier = super().save(commit=False)
        
        # Acesso seguro à chave 'password'
        password = self.cleaned_data.get('password')
        if password and commit:
            user = User.objects.create_user(
                username=self.cleaned_data.get('email'), 
                email=self.cleaned_data.get('email'),
                password=password
            )
            # Isso pressupõe que você tem um campo user no modelo Supplier para relacionar o usuário
            supplier.user = user
            supplier.save()
        return supplier
