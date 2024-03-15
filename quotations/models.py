from django.db import models
from products.models import Product
from suppliers.models import Supplier


class VolumeType(models.Model):
    nome = models.CharField(max_length=50)

    def __str__(self):
        return self.nome
   

class Cotation(models.Model):
    nome = models.CharField(max_length=255)
    data_abertura = models.DateField()
    data_fechamento = models.DateField()
    produtos = models.ManyToManyField(Product, through='CotationProduct')

    def __str__(self):
        return self.nome


class CotationProduct(models.Model):
    cotation = models.ForeignKey(Cotation, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    tipo_volume = models.ForeignKey(VolumeType, on_delete=models.CASCADE)
    observacao = models.TextField(blank=True, null=True)
    preco_7_dias = models.DecimalField(max_digits=6, decimal_places=3)
    preco_14_dias = models.DecimalField(max_digits=6, decimal_places=3)
    preco_21_dias = models.DecimalField(max_digits=6, decimal_places=3)
    preco_28_dias = models.DecimalField(max_digits=6, decimal_places=3)

    def __str__(self):
        return f'{self.product.name} em {self.cotation.nome}'
