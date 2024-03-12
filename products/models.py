from django.db import models


class Brand(models.Model):

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
        

class Product(models.Model):

    id = models.AutoField(primary_key=True)
    ean = models.CharField(max_length=13, unique=True)
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='product_brand', blank=False, null=False)
    photo = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name