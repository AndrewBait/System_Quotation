from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib import messages
# from suppliers.models import Supplier
from simple_history.models import HistoricalRecords


class Embalagem(models.Model):
    altura = models.DecimalField(max_digits=10, decimal_places=2)
    largura = models.DecimalField(max_digits=10, decimal_places=2)
    comprimento = models.DecimalField(max_digits=10, decimal_places=2)
    espessura = models.DecimalField(max_digits=10, decimal_places=2)
    raio = models.DecimalField(max_digits=10, decimal_places=2)

    UNIDADE_CHOICES = (
        ('mm', 'Milímetro'),
        ('cm', 'Centímetro'),
        ('m', 'Metro'),
    )
    unidade = models.CharField(max_length=2, choices=UNIDADE_CHOICES)
    
    def clean(self):
        for field in ['altura', 'largura', 'comprimento', 'espessura', 'raio']:
            value = getattr(self, field)
            if value is not None and value <= 0:
                raise ValidationError({field: _('O valor deve ser positivo.')})


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


class Brand(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name   
    
    
class Category(models.Model):
    department = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    

class ProductLine(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

      

class Product(models.Model):
    UNIDADE_CHOICES = (
        ('mm', 'Milímetro'),
        ('cm', 'Centímetro'),
        ('m', 'Metro'),       
    )

    UNIDADE_DE_MEDIDA_CHOICES = [
        ('Kg', 'Quilo'),
        ('Dp', 'Display'),
        ('Un', 'Unidade'),
        ('Cx', 'Caixa'),
        ('Fd', 'Fardo'),
        ('Pct', 'Pacote'),
        ('Sch', 'Sache'),
        ('Tp', 'Take Profit'),
    ]
    
    id = models.AutoField(primary_key=True)
    ean = models.CharField(max_length=13, unique=True, blank=True, null=True)
    sku = models.CharField("SKU", max_length=255, unique=True, blank=True, null=True)
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    product_line = models.ForeignKey(ProductLine, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    department = models.ForeignKey(Departamento, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    status = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='products/', blank=True, null=True)
    notas = models.TextField("Notas", blank=True, null=True)
    descricao = models.TextField(_("Descrição"), max_length=50, blank=True)
    preco_de_custo = models.DecimalField(_("Preço de Custo"), max_digits=10, decimal_places=3, blank=True, null=True)
    altura_embalagem = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, verbose_name='Altura da Embalagem')
    largura_embalagem = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, verbose_name='Largura da Embalagem')
    comprimento_embalagem = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, verbose_name='Comprimento da Embalagem')
    espessura_embalagem = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, verbose_name='Espessura da Embalagem')
    raio_embalagem = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True, verbose_name='Raio da Embalagem')
    unidade_altura = models.CharField(max_length=2, choices=UNIDADE_CHOICES, blank=True, null=True, verbose_name='Unidade de Medida Altura')
    unidade_largura = models.CharField(max_length=2, choices=UNIDADE_CHOICES, blank=True, null=True, verbose_name='Unidade de Medida Largura')
    unidade_comprimento = models.CharField(max_length=2, choices=UNIDADE_CHOICES, blank=True, null=True, verbose_name='Unidade de Medida Comprimento')
    unidade_espessura = models.CharField(max_length=2, choices=UNIDADE_CHOICES, blank=True, null=True, verbose_name='Unidade de Medida Espessura')
    unidade_raio = models.CharField(max_length=2, choices=UNIDADE_CHOICES, blank=True, null=True, verbose_name='Unidade de Medida Raio')
    unidade_de_medida = models.CharField(_("Unidade de Medida"), max_length=50, blank=True, null=True, choices=UNIDADE_DE_MEDIDA_CHOICES)
    quantidade_por_volume = models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade por Volume')
    data_de_validade = models.DateField(_("Data de Validade"), blank=True, null=True)
    history = HistoricalRecords()

    def clean(self):
        if self.ean and len(self.ean) != 13:
            raise ValidationError({'ean': "O EAN deve conter no máximo 13 dígitos."})
        
        if self.unidade_de_medida in ['Dp', 'Cx', 'Fd', 'Pct', 'Tp'] and not self.quantidade_por_volume:
            raise ValidationError("Para as unidades de medida Display, Caixa, Fardo, Pacote, e Take Profit, a quantidade por volume é obrigatória.")
        
        if self.unidade_de_medida not in ['Dp', 'Cx', 'Fd', 'Pct', 'Tp'] and self.quantidade_por_volume:
            raise ValidationError("A quantidade por volume só deve ser preenchida para as unidades de medida Display, Caixa, Fardo, Pacote, e Take Profit.")
        
        for field in ['altura_embalagem', 'largura_embalagem', 'comprimento_embalagem', 'espessura_embalagem', 'raio_embalagem', 'preco_de_custo']:
            value = getattr(self, field)
            if value is not None and value <= 0:
                raise ValidationError({field: _('O valor deve ser positivo.')})
        
        query = Product.objects.filter(name=self.name, category=self.category, subcategory=self.subcategory)
        if self.pk:
            query = query.exclude(pk=self.pk)
        
        if query.exists():
            raise ValidationError("Um produto com este nome, categoria e subcategoria já existe.")
        
        if self.ean and Product.objects.filter(ean=self.ean).exclude(pk=self.pk).exists():
            raise ValidationError({'ean': "Um produto com este código EAN já existe."})
        
        if self.sku and Product.objects.filter(sku=self.sku).exclude(pk=self.pk).exists():
            raise ValidationError({'sku': "Um produto com este código SKU já existe."})
        

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


from django.db import models
from django.utils.translation import gettext_lazy as _
from suppliers.models import Supplier  # Importar o modelo Supplier

class ProductPriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(_("Preço de Custo"), max_digits=10, decimal_places=3)
    date = models.DateField(_("Data da Atualização"))
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.SET_NULL, null=True, blank=True, related_name='price_history')

    class Meta:
        ordering = ['-date']
        get_latest_by = 'date'

    def __str__(self):
        return f"{self.product.name} - {self.price} em {self.date}"