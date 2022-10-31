# Generated by Django 4.1.1 on 2022-10-29 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0005_alter_offers_options_remove_offers_max_offer_price_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="offers",
            name="category",
            field=models.ManyToManyField(blank=True, null=True, to="shop.category"),
        ),
        migrations.AlterField(
            model_name="offers",
            name="end_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="offers",
            name="products",
            field=models.ManyToManyField(blank=True, null=True, to="shop.product"),
        ),
        migrations.AlterField(
            model_name="offers",
            name="start_date",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
