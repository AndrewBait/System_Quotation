# Generated by Django 5.0.2 on 2024-05-27 16:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_alter_productpricehistory_date'),
        ('suppliers', '0022_alter_supplier_comments'),
    ]

    operations = [
        migrations.AddField(
            model_name='productpricehistory',
            name='supplier',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='price_history', to='suppliers.supplier'),
        ),
    ]