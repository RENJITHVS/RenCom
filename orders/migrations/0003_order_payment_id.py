# Generated by Django 4.1.1 on 2022-10-26 19:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0002_alter_orderitem_order_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="payment_id",
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]