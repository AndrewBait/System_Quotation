from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _  
import uuid
from products.models import Departamento



class Cotacao(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=200)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True, related_name='cotacoes')
    data_abertura = models.DateField()
    data_fechamento = models.DateField()    
    status = models.CharField(max_length=10, default='ativo', choices=[('ativo', 'Ativo'), ('inativo', 'Inativo')])
    prazo_aviso = models.IntegerField(
                                        choices=[(7, '7 dias'), (14, '14 dias'), (21, '21 dias'), (28, '28 dias')],
                                        default=21,
                                        help_text='Prazo para os produtos'
                                    )
    
    def clean(self):
        # Garanta que data_abertura e data_fechamento não sejam None
        if self.data_abertura is None or self.data_fechamento is None:
            raise ValidationError("As datas de abertura e fechamento não podem ser nulas.")

        # Verifica se a data de fechamento é anterior à data de abertura
        if self.data_abertura > self.data_fechamento:
            raise ValidationError("A data de fechamento não pode ser anterior à data de abertura.")

    def __str__(self):
        return f"{self.nome} ({self.departamento.nome})"
    
def clean(self):
    data_inicio = self.data_abertura
    data_fim = self.data_fechamento

    # Verifique se alguma das datas é None antes de comparar
    if data_inicio is not None and data_fim is not None:
        if data_inicio > data_fim:
            raise ValidationError("A data de abertura não pode ser posterior à data de fechamento.")
        


    class Meta:
        verbose_name = _('Cotação')
        verbose_name_plural = _('Cotações')
        ordering = ['-data_abertura'] 

    
        # Posso adicionr aqui mais validaçoes caso for necessário

    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)

class ItemCotacao(models.Model):

    TIPO_VOLUME_CHOICES = (
        ('Kg', 'Quilo'),
        ('L', 'Litro'),
        ('Dp', 'Display'),
        ('Un', 'Unidade'),
        ('Cx', 'Caixa'),
        ('Fd', 'Fardo'),
        ('Bd', 'Bandeija'),
        ('Pc', 'Pacote'),
        ('Sc', 'Sache'),
        ('Tp', 'Take Profit'),
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

    
    def get_status_class(self):
        return 'btn-success' if self.status == 'aberta' else 'btn-secondary'

    def get_status_action(self):
        return 'Fechar' if self.status == 'aberta' else 'Abrir'

    # método para alternar o status
    def toggle_status(self):
        self.status = 'fechada' if self.status == 'aberta' else 'aberta'
        self.save()

    



