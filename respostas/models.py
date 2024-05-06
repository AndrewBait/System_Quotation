from django.db import models
from cotacao.models import Cotacao, ItemCotacao
from suppliers.models import Supplier
from products.models import Product



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
        

class Pedido(models.Model):
    produto = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produto")
    quantidade = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Quantidade")
    tipo_volume = models.CharField(max_length=50, choices=Product.UNIDADE_CHOICES, verbose_name="Tipo de Volume")
    fornecedor = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="Fornecedor")
    preco = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Preço")
    data_requisicao = models.DateField(verbose_name="Data da Requisição")
    status = models.CharField(max_length=50, choices=[
        ('pendente', 'Pendente'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ], default='pendente', verbose_name="Status do Pedido")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")

    def __str__(self):
        return f"{self.produto.name} - {self.fornecedor.name}"

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"