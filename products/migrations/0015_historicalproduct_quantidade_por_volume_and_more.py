# Generated by Django 5.0.2 on 2024-05-27 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_productpricehistory_supplier'),
    ]

    operations = [
        migrations.AddField(
            model_name='historicalproduct',
            name='quantidade_por_volume',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade por Volume'),
        ),
        migrations.AddField(
            model_name='product',
            name='quantidade_por_volume',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Quantidade por Volume'),
        ),
    ]
