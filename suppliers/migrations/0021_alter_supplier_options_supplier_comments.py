# Generated by Django 5.0.2 on 2024-04-13 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('suppliers', '0020_alter_supplier_delivery_time_rating_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='supplier',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='supplier',
            name='comments',
            field=models.TextField(blank=True, max_length=255, null=True, verbose_name='Comentários'),
        ),
    ]