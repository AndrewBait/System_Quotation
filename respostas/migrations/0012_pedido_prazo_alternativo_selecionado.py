# Generated by Django 5.0.2 on 2024-06-03 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('respostas', '0011_alter_respostacotacao_prazo_alternativo'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='prazo_alternativo_selecionado',
            field=models.BooleanField(default=False, verbose_name='Prazo Alternativo Selecionado'),
        ),
    ]
