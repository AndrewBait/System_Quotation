# Generated by Django 5.0.2 on 2024-04-17 19:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotacao', '0021_alter_cotacao_options_alter_cotacao_prazo_aviso'),
        ('products', '0011_embalagem_espessura_embalagem_raio_and_more'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='itemcotacao',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='itemcotacao',
            name='observacao',
            field=models.TextField(blank=True, default='', help_text='Observações sobre o item', max_length=200, null=True, verbose_name='Observação'),
        ),
        migrations.AlterField(
            model_name='cotacao',
            name='departamento',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.departamento'),
        ),
        migrations.AlterField(
            model_name='itemcotacao',
            name='cotacao',
            field=models.ForeignKey(help_text='Cotação à qual o item pertence', on_delete=django.db.models.deletion.CASCADE, related_name='itens_cotacao', to='cotacao.cotacao', verbose_name='Cotação'),
        ),
        migrations.AlterUniqueTogether(
            name='itemcotacao',
            unique_together={('cotacao', 'produto', 'tipo_volume', 'observacao', 'quantidade')},
        ),
    ]