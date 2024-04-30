# Generated by Django 5.0.2 on 2024-04-29 22:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cotacao', '0035_remove_respostacotacao_cotacao_and_more'),
        ('suppliers', '0022_alter_supplier_comments'),
    ]

    operations = [
        migrations.CreateModel(
            name='RespostaFornecedor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('preco', models.DecimalField(decimal_places=3, max_digits=10)),
                ('observacao_fornecedor', models.TextField(blank=True, null=True)),
                ('fornecedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='suppliers.supplier')),
                ('item_cotacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='respostas', to='cotacao.itemcotacao')),
            ],
        ),
    ]
