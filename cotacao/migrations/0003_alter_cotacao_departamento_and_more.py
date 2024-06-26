# Generated by Django 5.0.2 on 2024-03-29 22:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotacao', '0002_alter_cotacao_options_alter_departamento_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotacao',
            name='departamento',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cotacoes', to='cotacao.departamento'),
        ),
        migrations.AlterField(
            model_name='itemcotacao',
            name='tipo_volume',
            field=models.CharField(choices=[('kg', 'Quilo(s)'), ('un', 'Unidade(s)'), ('cx', 'Caixa(s)'), ('dp', 'Display(s)'), ('fd', 'Fardo(s)')], default='un', max_length=2),
        ),
    ]
