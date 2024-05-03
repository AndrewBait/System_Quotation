from django.db import models
from cotacao.models import Cotacao, ItemCotacao
from suppliers.models import Supplier

class RespostaCotacao(models.Model):
    cotacao = models.ForeignKey(Cotacao, on_delete=models.CASCADE)
    fornecedor = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    data_resposta = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('cotacao', 'fornecedor')

class ItemRespostaCotacao(models.Model):
    resposta_cotacao = models.ForeignKey(RespostaCotacao, on_delete=models.CASCADE)
    item_cotacao = models.ForeignKey(ItemCotacao, on_delete=models.CASCADE)
    preco = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    observacao = models.TextField(blank=True)
    imagem = models.ImageField(upload_to='respostas/', blank=True, null=True)

    class Meta:
        unique_together = ('resposta_cotacao', 'item_cotacao')