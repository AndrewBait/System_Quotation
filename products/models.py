from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.contrib import messages


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
        

class Product(models.Model):

    id = models.AutoField(primary_key=True)
    ean = models.CharField(max_length=13, unique=True, blank=True, null=True)  # EAN não é mais obrigatório
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    department = models.ForeignKey(Departamento, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    subcategory = models.ForeignKey(Subcategory, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
    status = models.BooleanField(default=True)  # True para ativo, False para inativo
    photo = models.ImageField(upload_to='products/', blank=True, null=True)

    def clean(self):
        if self.ean and len(self.ean) != 13:
            raise ValidationError({'ean': "O EAN deve conter 13 dígitos."})
        if not self.ean:
            if Product.objects.filter(name=self.name, brand=self.brand, category=self.category).exists():
                raise ValidationError("Um produto com este nome, marca e categoria já existe.")



    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name