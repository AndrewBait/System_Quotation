# Generated by Django 5.0.2 on 2024-06-03 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('respostas', '0014_remove_pedido_prazo_alternativo'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='prazo_alternativo_usado',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Prazo Alternativo Usado'),
        ),
    ]
