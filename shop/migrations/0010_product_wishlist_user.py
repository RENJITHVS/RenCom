# Generated by Django 4.1.1 on 2022-10-05 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0005_address'),
        ('shop', '0009_alter_product_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='wishlist_user',
            field=models.ManyToManyField(blank=True, related_name='user_wishlist', to='customers.customerprofile'),
        ),
    ]