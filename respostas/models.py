from django.db import models
from cotacao.models import Cotacao, ItemCotacao
from suppliers.models import Supplier
from products.models import Product
from django.conf import settings



class RespostaCotacao(models.Model):
    cotacao = models.ForeignKey(Cotacao, on_delete=models.CASCADE)
    fornecedor = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    data_resposta = models.DateTimeField(auto_now_add=True)
    prazo_alternativo = models.IntegerField(choices=[
        (0, 'À vista'),
        (7, '7 dias'),
        (14, '14 dias'),
        (21, '21 dias'),
        (28, '28 dias'),
    ], blank=True, null=True)


    class Meta:
        unique_together = ('cotacao', 'fornecedor')

class ItemRespostaCotacao(models.Model):
    resposta_cotacao = models.ForeignKey(RespostaCotacao, on_delete=models.CASCADE)
    item_cotacao = models.ForeignKey(ItemCotacao, on_delete=models.CASCADE)
    preco = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    prazo = models.PositiveIntegerField(null=True, blank=True)  # Prazo original
    preco_prazo_alternativo = models.DecimalField(max_digits=10, decimal_places=3, null=True, blank=True)
    prazo_alternativo = models.PositiveIntegerField(null=True, blank=True)  # Novo campo para prazo alternativo
    observacao = models.TextField(blank=True)
    imagem = models.ImageField(upload_to='respostas/', blank=True, null=True)

    class Meta:
        unique_together = ('resposta_cotacao', 'item_cotacao')
        

class PedidoAgrupado(models.Model):
    fornecedor = models.ForeignKey(Supplier, on_delete=models.CASCADE, verbose_name="Fornecedor")
    cotacao = models.ForeignKey(Cotacao, on_delete=models.CASCADE)
    data_requisicao = models.DateField(verbose_name="Data da Requisição")
    status = models.CharField(max_length=50, choices=[
        ('pendente', 'Pendente'),
        ('concluido', 'Concluído'),
        ('cancelado', 'Cancelado'),
    ], default='pendente', verbose_name="Status do Pedido")
    usuario_criador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    @property
    def vendedor(self):
        return self.fornecedor.vendedor

    @property
    def total_itens(self):
        return self.pedidos.count()

    @property
    def preco_total(self):
        return sum(item.preco_total for item in self.pedidos.all())

    def __str__(self):
        return f"{self.cotacao.nome} - {self.fornecedor.name}"

class Pedido(models.Model):
    produto = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Produto")
    quantidade = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Quantidade")
    tipo_volume = models.CharField(max_length=50, choices=Product.UNIDADE_CHOICES, verbose_name="Tipo de Volume")
    preco = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Preço")
    prazo_alternativo_selecionado = models.BooleanField(default=False, verbose_name="Prazo Alternativo Selecionado")
    prazo_alternativo = models.PositiveIntegerField(null=True, blank=True, verbose_name="Prazo Alternativo")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    pedido_agrupado = models.ForeignKey(PedidoAgrupado, related_name='pedidos', on_delete=models.CASCADE, verbose_name="Pedido Agrupado", null=True, default=None)

    def __str__(self):
        return f"{self.produto.name} - Quantidade: {self.quantidade}"


    @property
    def preco_total(self):
        if self.tipo_volume in ['Cx', 'Dp', 'Fd', 'Pct', 'Tp']:  # Tipos de volume que consideram quantidade por volume
            quantidade_unitaria = self.produto.quantidade_por_volume or 1
            return self.preco * self.quantidade * quantidade_unitaria
        elif self.tipo_volume == 'Kg':  # Considerando que 'Kg' representa quilo
            return self.preco * self.quantidade
        else:
            return self.preco * self.quantidade


    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"

