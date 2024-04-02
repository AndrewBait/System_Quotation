from django.db import models
from django.core.exceptions import ValidationError


class Brand(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    

class Department(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Category(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='categories')
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
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='products', blank=True, null=True)
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