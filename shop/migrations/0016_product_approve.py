# Generated by Django 4.1.1 on 2022-10-09 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0015_remove_product_author_alter_product_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='approve',
            field=models.BooleanField(default=False),
        ),
    ]
