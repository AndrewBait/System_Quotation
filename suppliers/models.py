from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from validate_docbr import CNPJ
from django.contrib.auth.models import User
from django.conf import settings


# Função de validação do CNPJ
def validate_cnpj(value):
    cnpj_validator = CNPJ()
    if not cnpj_validator.validate(value):
        raise ValidationError("CNPJ inválido.")


class Supplier(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(regex=r'^\+?\d{10,15}$', message="Número de telefone no formato: '+999999999'. Até 15 dígitos.")
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    company = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True, validators=[validate_cnpj], null=True)

    def __str__(self):
        return self.name
