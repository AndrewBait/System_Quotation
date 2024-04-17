# Generated by Django 5.0.2 on 2024-04-17 20:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotacao', '0025_alter_itemcotacao_quantidade'),
        ('products', '0011_embalagem_espessura_embalagem_raio_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemcotacao',
            name='produto',
            field=models.ForeignKey(help_text='Produto da cotação', on_delete=django.db.models.deletion.CASCADE, related_name='itens_cotacao', to='products.product', verbose_name='Produto'),
        ),
        migrations.AlterField(
            model_name='itemcotacao',
            name='tipo_volume',
            field=models.CharField(choices=[('Kg', 'Quilo'), ('L', 'Litro'), ('Dp', 'Display'), ('Un', 'Unidade'), ('Cx', 'Caixa'), ('Fd', 'Fardo'), ('Bd', 'Bandeija'), ('Pc', 'Pacote'), ('Sc', 'Sache'), ('Tp', 'Take Profit')], default='un', help_text='Tipo de volume do produto', max_length=2, verbose_name='Tipo de Volume'),
        ),
    ]