# Generated by Django 5.0.2 on 2024-04-15 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cotacao', '0018_alter_cotacao_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cotacao',
            name='status',
            field=models.CharField(choices=[('ativo', 'Ativo'), ('inativo', 'Inativo')], default='ativo', max_length=10),
        ),
    ]
