from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from validate_docbr import CNPJ
from django.contrib.auth.models import User
from django.conf import settings
from products.models import Departamento, Category, Subcategory, Brand
from django.core.validators import MinValueValidator
import datetime

def validate_cnpj(value):
    cnpj_validator = CNPJ()
    if not cnpj_validator.validate(value):
        raise ValidationError("CNPJ inválido.")

class Supplier(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
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
    holiday_cover_name = models.CharField("Nome do Fornecedor de Férias", max_length=255, null=True, blank=True)
    holiday_cover_email = models.EmailField("Email do Fornecedor de Férias", null=True, blank=True)
    holiday_cover_phone = models.CharField("Telefone do Fornecedor de Férias", validators=[phone_regex], max_length=17, blank=True, null=True)
    observation = models.TextField("Observação", null=True, blank=True)
    delivery_days = models.CharField("Dias de Entrega", max_length=100, blank=True, null=True)
    quality_rating = models.IntegerField(default=0, blank=True, null=True)
    delivery_time_rating = models.IntegerField(default=0, blank=True, null=True)
    price_rating = models.IntegerField(default=0, blank=True, null=True)
    reliability_rating = models.IntegerField(default=0, blank=True, null=True)
    flexibility_rating = models.IntegerField(default=0, blank=True, null=True)
    partnership_rating = models.IntegerField(default=0, blank=True, null=True)
    comments = models.TextField("Comentários", max_length=100, blank=True, null=True)
    billing_deadline_choices = [
        ('1-2', '1 a 2 dias úteis'),
        ('3-5', '3 a 5 dias úteis'),
        ('6-10', '6 a 10 dias úteis'),
        ('11-15', '11 a 15 dias úteis'),
        ('15+', 'Mais de 15 dias úteis'),
        ('negotiable', 'A combinar')
    ]
    billing_deadline = models.CharField(max_length=20, choices=billing_deadline_choices, default='1-2', verbose_name="Prazo de Faturamento")
    specific_billing_deadline = models.CharField(max_length=50, blank=True, null=True, verbose_name="Prazo Específico de Faturamento")
    
    @property
    def billing_deadline_display(self):
        return dict(self.billing_deadline_choices).get(self.billing_deadline, '')

    @property
    def delivery_days_display(self):
        return ', '.join(self.delivery_days.split(',')) if self.delivery_days else ''

    class Meta:
        ordering = ['name']

    def get_departments(self):
        return ", ".join([d.name for d in self.departments.all()])

    def average_rating(self):
        ratings = [self.quality_rating, self.delivery_time_rating, self.flexibility_rating, self.partnership_rating]
        ratings = [rating for rating in ratings if rating is not None]
        if ratings:
            return sum(ratings) / len(ratings)
        return None

    def __str__(self):
        return self.name
