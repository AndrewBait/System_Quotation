from django.db import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from validate_docbr import CNPJ

# Função de validação do CNPJ
def validate_cnpj(value):
    cnpj_validator = CNPJ()
    if not cnpj_validator.validate(value):
        raise ValidationError("CNPJ inválido.")

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)

    # Validador para telefone
    phone_regex = RegexValidator(regex=r'^\+55\d{2}\d{4,5}\d{4}$', message="O número de telefone deve ser no formato: '+999999999'. Até 15 dígitos permitidos.")
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)

    company = models.CharField(max_length=255)
    # Adiciona a função de validação ao campo cnpj
    cnpj = models.CharField(max_length=18, unique=True, validators=[validate_cnpj], null=True)

    def __str__(self):
        return self.name
