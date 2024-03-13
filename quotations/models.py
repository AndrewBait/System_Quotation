from django.db import models
from products.models import Product
from suppliers.models import Supplier

class

class Cotation(models.Model):
    nome = models.CharField(max_length=255)
    data_abertura = models.DateField()
    data_fechamento = models.DateField()
    observacao = models.TextField(blank=True, null=True)
    produtos = models.ManyToManyField(Product, through='CotationProduct')

    def __str__(self):
        return self.nome

class CotationProduct(models.Model):
    cotation = models.ForeignKey(Cotation, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    tipo_volume = models.CharField(max_length=50) # Exemplo: 'caixa', 'unidade', 'quilo'

    def __str__(self):
        return f'{self.product.name} em {self.cotation.nome}'
