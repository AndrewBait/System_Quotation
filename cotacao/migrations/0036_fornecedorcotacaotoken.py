# Generated by Django 5.0.2 on 2024-05-03 13:21

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotacao', '0035_remove_respostacotacao_cotacao_and_more'),
        ('suppliers', '0022_alter_supplier_comments'),
    ]

    operations = [
        migrations.CreateModel(
            name='FornecedorCotacaoToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('cotacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cotacao.cotacao')),
                ('fornecedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='suppliers.supplier')),
            ],
        ),
    ]
