# Generated by Django 5.0.2 on 2024-03-30 14:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cotacao', '0009_delete_respostafornecedor'),
        ('suppliers', '0002_supplier_cnpj_alter_supplier_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('item_cotacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='cotacao.itemcotacao')),
                ('supplier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supplier_answers', to='suppliers.supplier')),
            ],
        ),
    ]
