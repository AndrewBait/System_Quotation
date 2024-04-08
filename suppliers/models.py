from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from validate_docbr import CNPJ
from django.contrib.auth.models import User
from django.conf import settings
from products.models import Departamento, Category, Subcategory, Brand
from django.core.validators import MinValueValidator
import datetime


# Função de validação do CNPJ
def validate_cnpj(value):
    cnpj_validator = CNPJ()
    if not cnpj_validator.validate(value):
        raise ValidationError("CNPJ inválido.")
    

class Supplier(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(regex=r'^\+?\d{10,15}$', message="Número de telefone no formato: '+999999999'. Até 15 dígitos.", )
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    company = models.CharField(max_length=255, null=True, blank=True)
    cnpj = models.CharField(max_length=18, unique=True, validators=[validate_cnpj], null=True, blank=True)
    active = models.BooleanField(default=True, verbose_name="Ativo")
    address_line_1 = models.CharField("Endereço", max_length=255, null=True, blank=True)
    address_line_2 = models.CharField("Complemento", max_length=255, null=True, blank=True)
    city = models.CharField("Cidade", max_length=100, null=True, blank=True)
    state = models.CharField("Estado", max_length=50, null=True, blank=True)
    zip_code = models.CharField("CEP", max_length=10, null=True, blank=True)
    minimum_order_value = models.DecimalField("Valor Mínimo para Pedido", max_digits=10, decimal_places=3, validators=[MinValueValidator(0)], null=True, blank=True)
    order_response_deadline = models.TimeField("Prazo de Resposta para Pedidos", null=True, blank=True)
    departments = models.ManyToManyField('products.Departamento', related_name='suppliers', blank=True)
    categories = models.ManyToManyField(Category, blank=True, verbose_name="Categorias")
    subcategories = models.ManyToManyField(Subcategory, blank=True, verbose_name="Subcategorias")
    brands = models.ManyToManyField(Brand,  blank=True, verbose_name="Marcas")
    created_at = models.DateTimeField(auto_now_add=False, default=datetime.datetime.now, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    deleted = models.BooleanField(default=False)

    def get_departments(self):
        return ", ".join([d.name for d in self.departments.all()])



    def __str__(self):
        return self.name

