# Generated by Django 4.1.1 on 2022-10-06 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='vendors',
        ),
        migrations.AddField(
            model_name='order',
            name='email',
            field=models.CharField(blank=True, max_length=254),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_option',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
