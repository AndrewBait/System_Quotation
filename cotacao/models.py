from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import uuid
from products.models import Departamento

class Cotacao(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    nome = models.CharField(max_length=200)
    departamento = models.ForeignKey(Departamento, on_delete=models.SET_NULL, null=True )
    usuario_criador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cotacoes_criadas', null=True, )
    data_abertura = models.DateField()
    data_fechamento = models.DateField()    
    status = models.CharField(max_length=10, default='ativo', choices=[('ativo', 'Ativo'), ('inativo', 'Inativo')])
    prazo = models.IntegerField(
                                    choices=[(0, 'à vista'), (7, '7 dias'), (14, '14 dias'), (21, '21 dias'), (28, '28 dias')],
                                    default=21,
                                    help_text='Prazo para os produtos'
                                    )
    
    def clean(self):
        super().clean()
        if self.status == 'inativo' and not self._state.adding:
            raise ValidationError("Não é possível editar uma cotação inativa.")
        if self.data_abertura > self.data_fechamento:
            raise ValidationError(_("A data de fechamento não pode ser anterior à data de abertura."))
        if self.status not in ['ativo', 'inativo']:
            raise ValidationError(_("Status inválido. Escolha entre 'ativo' e 'inativo'."))

    def __str__(self):
        return f"{self.nome} ({self.departamento.nome})"      


    class Meta:
        verbose_name = _('Cotação')
        verbose_name_plural = _('Cotações')
        ordering = ['data_abertura']
        indexes = [
            models.Index(fields=['departamento']),
            models.Index(fields=['status']),
            models.Index(fields=['data_abertura']),
        ]
        

class ItemCotacao(models.Model):
    
    cotacao = models.ForeignKey(Cotacao, on_delete=models.CASCADE, related_name='itens_cotacao', verbose_name='Cotação', help_text='Cotação à qual o item pertence')
    produto = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name='Produto', help_text='Produto da cotação', related_name='itens_cotacao', blank=False, null=False)
    quantidade = models.PositiveIntegerField(default=1, verbose_name='Quantidade', help_text='Quantidade do produto', blank=False, null=False)
    tipo_volume = models.CharField(max_length=2, choices=[('Kg', 'Quilo'), ('L', 'Litro'), ('Dp', 'Display'), ('Un', 'Unidade'), ('Cx', 'Caixa'), ('Fd', 'Fardo'), ('Bd', 'Bandeija'), ('Pc', 'Pacote'), ('Sc', 'Sache'), ('Tp', 'Take Profit'),], default='un', verbose_name='Tipo de Volume', help_text='Tipo de volume do produto', blank=False, null=False)
    observacao = models.TextField(blank=True, null=True, default='', verbose_name='Observação', help_text='Observações sobre o item', max_length=100)
    

    def __str__(self):
        return f"{self.quantidade}x {self.produto.name} [{self.get_tipo_volume_display()}] na cotação {self.cotacao.nome} ({self.cotacao.departamento.nome}) "

    class Meta:
        verbose_name = _('Item de Cotação')
        verbose_name_plural = _('Itens de Cotação')
        ordering = ['produto__name']
        unique_together = ('cotacao', 'produto', 'tipo_volume', 'observacao', 'quantidade')
        indexes = [
            models.Index(fields=['produto']),
            models.Index(fields=['cotacao']),
        ]

    def clean(self):
        super().clean()
        if self.quantidade <= 0:
            raise ValidationError(_('A quantidade deve ser maior que zero.'))
        
        # Verifica se o produto já foi adicionado à mesma cotação
        exists = ItemCotacao.objects.filter(
            cotacao=self.cotacao,
            produto=self.produto
        ).exclude(pk=self.pk).exists()
        if exists:
            raise ValidationError(_('Este produto já foi adicionado à cotação.'))

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

    



