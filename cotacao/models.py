from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _  
import uuid


class Departamento(models.Model):
    nome = models.CharField(max_length=100, unique=True)  

    def delete(self, *args, **kwargs):
        if self.cotacoes.exists():
            raise ValidationError("Não é possível excluir um departamento que possui cotações vinculadas.")
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = _('Departamento')
        verbose_name_plural = _('Departamentos')
        ordering = ['nome']  

class Cotacao(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=200)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, related_name='cotacoes')
    data_abertura = models.DateField()
    data_fechamento = models.DateField()


    def __str__(self):
        return f"{self.nome} ({self.departamento.nome})"

    class Meta:
        verbose_name = _('Cotação')
        verbose_name_plural = _('Cotações')
        ordering = ['-data_abertura'] 

    def clean(self):

        if self.data_fechamento < self.data_abertura:
            raise ValidationError(_('A data de fechamento não pode ser anterior à data de abertura.'))

        # Posso adicionr aqui mais validaçoes caso for necessário

    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)

class ItemCotacao(models.Model):

    TIPO_VOLUME_CHOICES = (
        ('kg', 'Quilo(s)'),
        ('un', 'Unidade(s)'),
        ('cx', 'Caixa(s)'),
        ('dp', 'Display(s)'),
        ('fd', 'Fardo(s)'),
    )

    cotacao = models.ForeignKey(Cotacao, on_delete=models.CASCADE, related_name='itens_cotacao')
    produto = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)
    tipo_volume = models.CharField(max_length=2, choices=TIPO_VOLUME_CHOICES, default='un')

    def __str__(self):
        return f"{self.quantidade}x {self.produto.name} [{self.get_tipo_volume_display()}]"

    class Meta:
        verbose_name = _('Item de Cotação')
        verbose_name_plural = _('Itens de Cotação')
        ordering = ['produto__name']
        unique_together = ('cotacao', 'produto', 'tipo_volume') 

    def clean(self):
  
        if self.quantidade <= 0:
            raise ValidationError(_('A quantidade deve ser maior que zero.'))

    def save(self, *args, **kwargs):
        self.full_clean()  
        super().save(*args, **kwargs)



