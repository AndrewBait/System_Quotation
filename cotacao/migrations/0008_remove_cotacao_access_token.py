# Generated by Django 5.0.2 on 2024-03-30 02:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cotacao', '0007_cotacao_access_token_respostafornecedor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cotacao',
            name='access_token',
        ),
    ]
