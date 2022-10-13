# Generated by Django 4.1.1 on 2022-10-10 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0016_product_approve'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='in_stock',
        ),
        migrations.AddField(
            model_name='productattribute',
            name='in_stock',
            field=models.BooleanField(default=True, verbose_name='Product in stock'),
        ),
    ]