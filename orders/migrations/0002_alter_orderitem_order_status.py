# Generated by Django 4.1.1 on 2022-10-22 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderitem",
            name="order_status",
            field=models.CharField(
                choices=[
                    ("In Process", "In Process"),
                    ("Shipped", "Shipped"),
                    ("Delivered", "Delivered"),
                    ("Cancelled", "Cancelled"),
                ],
                default="In process",
                max_length=150,
            ),
        ),
    ]
