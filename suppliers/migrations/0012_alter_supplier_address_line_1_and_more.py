# Generated by Django 5.0.2 on 2024-04-08 02:28

import datetime
import suppliers.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_remove_product_fornecedores'),
        ('suppliers', '0011_alter_supplier_departments_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supplier',
            name='address_line_1',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Endereço'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='address_line_2',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Complemento'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='brands',
            field=models.ManyToManyField(blank=True, null=True, to='products.brand', verbose_name='Marcas'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='categories',
            field=models.ManyToManyField(blank=True, null=True, to='products.category', verbose_name='Categorias'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Cidade'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='cnpj',
            field=models.CharField(blank=True, max_length=18, null=True, unique=True, validators=[suppliers.models.validate_cnpj]),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='company',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='created_at',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now, null=True),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='state',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Estado'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='subcategories',
            field=models.ManyToManyField(blank=True, null=True, to='products.subcategory', verbose_name='Subcategorias'),
        ),
        migrations.AlterField(
            model_name='supplier',
            name='zip_code',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='CEP'),
        ),
    ]
