from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _  # Para tradução dos textos de erro
from django.utils import timezone  # Para validações de data


class Departamento(models.Model):
    nome = models.CharField(max_length=100, unique=True)  # Garante que cada departamento tenha um nome único

    def __str__(self):
        return self.nome

    class Meta:
        verbose_name = _('Departamento')
        verbose_name_plural = _('Departamentos')
        ordering = ['nome']  # Ordena os departamentos por nome por padrão

class Cotacao(models.Model):
    nome = models.CharField(max_length=200)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='cotacoes')
    data_abertura = models.DateField()
    data_fechamento = models.DateField()

    def __str__(self):
        return f"{self.nome} ({self.departamento.nome})"

    class Meta:
        verbose_name = _('Cotação')
        verbose_name_plural = _('Cotações')
        ordering = ['-data_abertura']  # Ordena as cotações pela data de abertura, das mais recentes às mais antigas

    def clean(self):
        # Validação para garantir que a data de fechamento não seja antes da data de abertura
        if self.data_fechamento < self.data_abertura:
            raise ValidationError(_('A data de fechamento não pode ser anterior à data de abertura.'))

        # Adicione aqui outras validações conforme necessário

    def save(self, *args, **kwargs):
        self.full_clean()  # Chama o método clean() antes de salvar
        super().save(*args, **kwargs)

class ItemCotacao(models.Model):
    # Definindo as opções de tipo de volume
    TIPO_VOLUME_CHOICES = (
        ('kg', 'Quilo'),
        ('un', 'Unidade'),
        ('cx', 'Caixa'),
        ('dp', 'Display'),
        ('fd', 'Fardo'),
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
        unique_together = ('cotacao', 'produto', 'tipo_volume')  # Atualizado para considerar tipo de volume

    def clean(self):
        # Verifica se a quantidade é positiva
        if self.quantidade <= 0:
            raise ValidationError(_('A quantidade deve ser maior que zero.'))

    def save(self, *args, **kwargs):
        self.full_clean()  # Garante a execução de validações antes de salvar
        super().save(*args, **kwargs)
