# Generated by Django 5.0.2 on 2024-05-22 00:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0011_embalagem_espessura_embalagem_raio_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productpricehistory',
            name='price',
            field=models.DecimalField(decimal_places=3, max_digits=10, verbose_name='Preço de Custo'),
        ),
    ]
