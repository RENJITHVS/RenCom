# Generated by Django 4.1.1 on 2022-10-13 07:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0024_remove_product_product_type_delete_producttype'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='brandName',
            new_name='Category',
        ),
    ]