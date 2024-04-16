from django import forms
from .models import Departamento, Category, Subcategory, Brand, Supplier
from django.core.exceptions import ValidationError
from .models import Supplier



class SupplierForm(forms.ModelForm):

   
    class Meta:
        model = Supplier
        fields = '__all__'  # Inclui todos os campos do modelo no formulário
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(00) 00000-0000'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0000-00'}),
            'active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'minimum_order_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01' ,'placeholder': '0.000,00'}),
            'order_response_deadline': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'departments': forms.Select(attrs={'class': 'form-control'}),
            'categories': forms.CheckboxSelectMultiple(),
            'subcategories': forms.CheckboxSelectMultiple(),
            'brands': forms.CheckboxSelectMultiple(),
            'holiday_cover_name': forms.TextInput(attrs={'class': 'form-control'}),
            'holiday_cover_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'holiday_cover_phone': forms.TextInput(attrs={'class': 'form-control'}),            
            'observation': forms.Textarea(attrs={'class': 'form-control'}),
            'active': forms.Select(choices=[(True, 'Ativo'), (False, 'Inativo')], attrs={'class': 'form-control'}),
            
        }
        exclude = ['deleted']  # Exclui o campo 'deleted' do formulário

    def clean_minimum_order_value(self): # Método de validação do campo minimum_order_value
        minimum_order_value = self.cleaned_data.get('minimum_order_value')
        if minimum_order_value is not None:
            if minimum_order_value < 0:  # Ou qualquer outra comparação
                raise forms.ValidationError("O valor mínimo do pedido deve ser maior ou igual a zero.") # Ou qualquer outra mensagem de erro
        return minimum_order_value # Sempre retorne o valor limpo
    
    def clean_quality_rating(self): # Método de validação do campo quality_rating
        quality_rating = self.cleaned_data.get('quality_rating')
        if quality_rating is not None:
            if not 0 <= quality_rating <= 5:
                raise forms.ValidationError("A avaliação de qualidade deve estar entre 0 e 5.")
        return quality_rating

    
class SupplierStatusFilterForm(forms.Form): # Formulário para filtrar fornecedores por status
    STATUS_CHOICES = [
        ('', 'Todos'),
        (True, 'Ativo'),
        (False, 'Inativo'),
    ]
    status = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label='Status', widget=forms.Select(attrs={'onchange': 'this.form.submit();'}))


class SupplierFilterForm(forms.Form): # Formulário para filtrar fornecedores
    STATUS_CHOICES = [('', 'Todos'), ('True', 'Ativo'), ('False', 'Inativo')]
    active = forms.ChoiceField(choices=STATUS_CHOICES, required=False, label='Status', widget=forms.Select(attrs={'onchange': 'this.form.submit();', 'class': 'form-select'})) # Campo para filtrar por status
    department = forms.ModelChoiceField(queryset=Departamento.objects.all(), required=False, label='Departamento', widget=forms.Select(attrs={'onchange': 'this.form.submit();', 'class': 'form-select'})) # Campo para filtrar por departamento
    category = forms.ModelChoiceField(queryset=Category.objects.none(), required=False, label='Categoria', widget=forms.Select(attrs={'class': 'form-select'})) # Campo para filtrar por categoria
    subcategory = forms.ModelChoiceField(queryset=Subcategory.objects.none(), required=False, label='Subcategoria', widget=forms.Select(attrs={'class': 'form-select'})) # Campo para filtrar por subcategoria
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(), required=False, label='Marca', widget=forms.Select(attrs={'onchange': 'this.form.submit();', 'class': 'form-select'})) # Campo para filtrar por marca
    
    def __init__(self, *args, **kwargs): # Método para inicializar o formulário
        super().__init__(*args, **kwargs) # Chama o método __init__ da classe pai
        if 'department' in self.data: # Se o campo department estiver presente nos dados do formulário
            try:
                department_id = int(self.data.get('department')) # Obtém o ID do departamento
                self.fields['category'].queryset = Category.objects.filter(department_id=department_id).order_by('name') # Filtra as categorias pelo departamento
                if 'category' in self.data: # Se o campo category estiver presente nos dados do formulário
                    category_id = int(self.data.get('category')) # Obtém o ID da categoria
                    self.fields['subcategory'].queryset = Subcategory.objects.filter(category_id=category_id).order_by('name') # Filtra as subcategorias pela categoria
            except (ValueError, TypeError): # Se houver erro ao converter o ID para inteiro
                pass  # invalid input; ignore and fallback to empty City queryset

class SupplierRatingsForm(forms.ModelForm): # Formulário para avaliar fornecedores
    class Meta: 
        model = Supplier
        fields = [
            'quality_rating', 'delivery_time_rating', 'price_rating',
            'reliability_rating', 'flexibility_rating', 'partnership_rating', 'comments'
        ]
        widgets = {
            'quality_rating': forms.HiddenInput(),
            'delivery_time_rating': forms.HiddenInput(),
            'price_rating': forms.HiddenInput(),
            'reliability_rating': forms.HiddenInput(),
            'flexibility_rating': forms.HiddenInput(),
            'partnership_rating': forms.HiddenInput(),
        }
