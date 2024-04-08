from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib import messages
# from suppliers.models import Supplier
from simple_history.models import HistoricalRecords


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

    id = models.AutoField(primary_key=True)
    ean = models.CharField(max_length=13, unique=True, blank=True, null=True)  # EAN não é mais obrigatório
    sku = models.CharField("SKU", max_length=255, unique=True, blank=True, null=True)
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    product_line = models.ForeignKey(ProductLine, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    department = models.ForeignKey(Departamento, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    status = models.BooleanField(default=True)  # True para ativo, False para inativo
    photo = models.ImageField(upload_to='products/', blank=True, null=True)
    notas = models.TextField("Notas", blank=True, null=True)
    # fornecedores = models.ManyToManyField(Supplier, related_name='produtos', blank=True, null=True)
    descricao = models.TextField(_("Descrição"), max_length=50, blank=True)
    preco_de_custo = models.DecimalField(_("Preço de Custo"), max_digits=10, decimal_places=2, blank=True, null=True)
    unidade_de_medida = models.CharField(_("Unidade de Medida"), max_length=50, blank=True, null=True, choices=[
        ('Kg', 'Quilo'),
        ('L', 'Litro'),
        ('Dp', 'Display'),
        ('Un', 'Unidade'),
        ('Cx', 'Caixa'),
        ('Fd', 'Fardo'),
        ('Bdj', 'Bandeija'),
        ('Pct', 'Pacote'),
        ('Sch', 'Sache'),
        ('Tp', 'Take Profit'),
        
    ])
    data_de_validade = models.DateField(_("Data de Validade"), blank=True, null=True)
    history = HistoricalRecords()

    def clean(self):
        if self.ean and len(self.ean) != 13:
            raise ValidationError({'ean': "O EAN deve conter no máximo 13 dígitos."})
        
        # Verifica se o produto com este nome, categoria e subcategoria já existe (excluindo o próprio objeto no caso de uma atualização).
        query = Product.objects.filter(name=self.name, category=self.category, subcategory=self.subcategory)
        if self.pk:  # Verifica se o objeto já tem um ID, indicando que é uma atualização.
            query = query.exclude(pk=self.pk)
        
        if query.exists():
            # Essa mudança permite que a validação de unicidade considere o caso de atualização, 
            # evitando considerar o próprio objeto como duplicata.
            raise ValidationError("Um produto com este nome, categoria e subcategoria já existe.")

        # Note: Não é necessário retornar nada, pois o método clean modifica o estado do objeto ou levanta uma exceção se houver erro.

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class ProductPriceHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(_("Preço de Custo"), max_digits=10, decimal_places=2)
    date = models.DateField(_("Data da Atualização"), auto_now_add=True)

    class Meta:
        ordering = ['-date']
        get_latest_by = 'date'

    def __str__(self):
        return f"{self.product.name} - {self.price} em {self.date}"