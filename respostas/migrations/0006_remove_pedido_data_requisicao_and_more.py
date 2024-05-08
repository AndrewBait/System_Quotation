# Generated by Django 5.0.2 on 2024-05-08 00:00

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotacao', '0037_alter_itemcotacao_tipo_volume'),
        ('respostas', '0005_pedido'),
        ('suppliers', '0022_alter_supplier_comments'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedido',
            name='data_requisicao',
        ),
        migrations.RemoveField(
            model_name='pedido',
            name='fornecedor',
        ),
        migrations.RemoveField(
            model_name='pedido',
            name='status',
        ),
        migrations.CreateModel(
            name='PedidoAgrupado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_requisicao', models.DateField(verbose_name='Data da Requisição')),
                ('status', models.CharField(choices=[('pendente', 'Pendente'), ('concluido', 'Concluído'), ('cancelado', 'Cancelado')], default='pendente', max_length=50, verbose_name='Status do Pedido')),
                ('cotacao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cotacao.cotacao')),
                ('fornecedor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='suppliers.supplier', verbose_name='Fornecedor')),
                ('usuario_criador', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='pedido',
            name='pedido_agrupado',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pedidos', to='respostas.pedidoagrupado', verbose_name='Pedido Agrupado'),
        ),
    ]